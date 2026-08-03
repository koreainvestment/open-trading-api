package tasks

import (
	"context"
	"encoding/json"
	"fmt"
	"github.com/kis-open-api/go/internal/dartfiling/config"
	"github.com/kis-open-api/go/internal/dartfiling/models"
	"github.com/kis-open-api/go/internal/external/dart"
	"github.com/kis-open-api/go/internal/external/openai"
	"github.com/kis-open-api/go/internal/external/xbrl"
	"log"
	"strings"
	"time"

	"github.com/hibiken/asynq"
	"gorm.io/gorm"
)

// TaskProcessor holds dependencies for our task handlers
type TaskProcessor struct {
	DB           *gorm.DB
	config       *config.Config
	dartClient   *dart.DartClient
	fileAnalyzer *openai.FileAnalyzer
}

// NewTaskProcessor creates a new TaskProcessor
func NewTaskProcessor(db *gorm.DB, config *config.Config) *TaskProcessor {
	return &TaskProcessor{
		DB:           db,
		config:       config,
		dartClient:   dart.New(config.DartAPIKey),
		fileAnalyzer: openai.NewFileAnalyzer(config.OpenAIAPIKey),
	}
}

func (p *TaskProcessor) HandleFetchReportsTask(ctx context.Context, t *asynq.Task) error {
	log.Println("Fetching reports")

	var payload FetchReportsPayload
	if err := json.Unmarshal(t.Payload(), &payload); err != nil {
		return fmt.Errorf("failed to unmarshal payload: %w", asynq.SkipRetry)
	}

	log.Printf("Fetching reports for %+v", payload)

	var pageInfos []dart.PageInfo
	if (payload.CorpCode != nil && *payload.CorpCode != "") || (payload.Limit != nil && *payload.Limit > 0) {
		info := dart.PageInfo{}
		if payload.CorpCode != nil {
			info.CorpCode = *payload.CorpCode
		}
		if payload.Limit != nil {
			info.Limit = *payload.Limit
		}
		pageInfos = append(pageInfos, info)
	}

	rawReports, err := p.dartClient.GetRecentRawReports(pageInfos...)
	if err != nil {
		log.Printf("failed to fetch reports: %v", err)
		return nil
	}

	totalUsedTokens := int64(0)
	var analyses []models.Analysis
	for _, rawReport := range rawReports {
		count, err := gorm.G[models.RawReport](p.DB).Where("receipt_number = ?", rawReport.RceptNo).Count(ctx, "id")
		if err != nil {
			return err
		}

		if count > 0 {
			log.Printf("raw report already exists: %s", rawReport.RceptNo)
			continue
		}

		rawDocument, err := p.dartClient.GetDocument(rawReport.RceptNo)
		if err == dart.ErrDocumentNotFound {
			log.Printf("document not found: %s %s %s %s", rawReport.RceptDt, rawReport.RceptNo, rawReport.CorpName, rawReport.ReportNm)
			continue
		}

		if err != nil {
			log.Printf("failed to get document: %v", err)
			return err
		}

		doc, err := xbrl.ParseXBRL([]byte(rawDocument))
		if err != nil {
			log.Printf("failed to parse XBRL document: %v", err)
			return err
		}

		j, err := json.MarshalIndent(doc, "", "  ")
		if err != nil {
			log.Printf("failed to marshal JSON: %v", err)
			return err
		}

		dbRawReport := models.RawReport{
			ReceiptNumber: rawReport.RceptNo,
			ReportName:    rawReport.ReportNm,
			CorpCode:      rawReport.CorpCode,
			BlobData:      []byte(rawDocument),
			BlobSize:      len(rawDocument),
			JSONData:      j,
		}

		result := gorm.WithResult()
		err = gorm.G[models.RawReport](p.DB, result).Create(ctx, &dbRawReport)
		if err != nil {
			return err
		}

		reportType := ""
		if strings.Contains(doc.ReportTitle, "분기보고서") || strings.Contains(doc.ReportTitle, "사업보고서") || strings.Contains(doc.ReportTitle, "반기보고서") {
			reportType = "report"
		} else {
			log.Printf("unknown report type: %s", doc.ReportTitle)
		}

		reportLength := len(j)
		var analysis interface{}
		var usedTokens int64
		if reportLength > openai.PreviewByteLimit {
			log.Printf("analyzing report with batch API: %s", dbRawReport.ReceiptNumber)
			analysis, usedTokens, err = p.fileAnalyzer.AnalyzeReportBatch(ctx, string(j), reportType)
			if err != nil {
				log.Printf("failed to analyze report: %v", err)
				continue
			}
		} else {
			analysis, usedTokens, err = p.fileAnalyzer.AnalyzeReport(ctx, string(j), reportType)
			if err != nil {
				log.Printf("failed to analyze report: %v", err)
				continue
			}
		}

		if v, ok := analysis.(*openai.DefaultReport); ok {
			if v.CompanyName == "" {
				company, err := gorm.G[models.Company](p.DB).Where("corp_code = ?", rawReport.CorpCode).First(ctx)
				if err != nil {
					log.Printf("company not found in DB for corp_code=%s (%v), using report CorpName", rawReport.CorpCode, err)
					v.CompanyName = rawReport.CorpName
				} else {
					v.CompanyName = company.CorpName
				}
			}

			if v.SchemaSuggestion != "" {
				structureJSON, err := json.Marshal(v.SchemaSuggestion)
				if err != nil {
					log.Printf("failed to marshal schema suggestion: %v", err)
					continue
				}

				rt := models.ReportType{
					Name:              v.Type,
					Structure:         json.RawMessage(structureJSON),
					SourceRawReportID: dbRawReport.ID,
				}

				result := gorm.WithResult()
				err = gorm.G[models.ReportType](p.DB, result).Create(ctx, &rt)
				if err != nil {
					return err
				}

				v.SchemaSuggestion = ""
				analysis = v
			}
		}

		analysisJSON, err := json.MarshalIndent(analysis, "", "  ")
		if err != nil {
			log.Printf("failed to marshal analysis: %v", err)
			continue
		}

		analyses = append(analyses, models.Analysis{
			RawReportID: dbRawReport.ID,
			UsedTokens:  usedTokens,
			Analysis:    analysisJSON,
		})

		log.Printf("processed raw report: %s, %s, %d, %d", dbRawReport.ReceiptNumber, dbRawReport.CorpCode, dbRawReport.BlobSize, usedTokens)

		totalUsedTokens += usedTokens

		log.Printf("total used tokens: %d", totalUsedTokens)
	}

	if len(analyses) > 0 {
		log.Printf("storing %d analyses in batch", len(analyses))
		result := gorm.WithResult()
		err := gorm.G[models.Analysis](p.DB, result).CreateInBatches(ctx, &analyses, len(analyses))
		if err != nil {
			log.Printf("failed to store analyses in batch: %v", err)
			return err
		}
		log.Printf("successfully stored %d analyses in batch", len(analyses))
	}

	log.Println("Reports fetched successfully")
	return nil
}

func (p *TaskProcessor) HandleFetchCompaniesTask(ctx context.Context, t *asynq.Task) error {
	log.Println("Fetching companies")

	var payload FetchCompaniesPayload
	if err := json.Unmarshal(t.Payload(), &payload); err != nil {
		return fmt.Errorf("failed to unmarshal payload: %w", asynq.SkipRetry)
	}

	log.Printf("Fetching companies")

	companies, err := p.dartClient.GetCompanies()
	if err != nil {
		log.Printf("failed to fetch companies: %v", err)
		return err
	}

	log.Printf("fetched %d companies", len(companies))

	for _, company := range companies {
		existingCompany, err := gorm.G[models.Company](p.DB).Where("corp_code = ?", company.CorpCode).First(ctx)
		if err == gorm.ErrRecordNotFound {
			lastModifiedDate, err := time.Parse("20060102", company.ModifyDate)
			if err != nil {
				log.Printf("failed to parse last modified date: %v", err)
				return err
			}
			company := models.Company{
				CorpCode:         company.CorpCode,
				CorpName:         company.CorpName,
				CorpEngName:      company.CorpEngName,
				LastModifiedDate: lastModifiedDate,
			}

			result := gorm.WithResult()
			err = gorm.G[models.Company](p.DB, result).Create(ctx, &company)
			if err != nil {
				return err
			}
			continue
		}

		if err != nil {
			return err
		}

		log.Printf("existingCompany: %+v", existingCompany)

		existingCompany.CorpName = company.CorpName
		existingCompany.CorpEngName = company.CorpEngName
		existingCompany.LastModifiedDate, err = time.Parse("20060102", company.ModifyDate)
		if err != nil {
			return err
		}

		result := gorm.WithResult()
		_, err = gorm.G[models.Company](p.DB, result).Updates(ctx, existingCompany)
		if err != nil {
			return err
		}
	}

	return nil
}

func (p *TaskProcessor) GetDartClient() *dart.DartClient {
	return p.dartClient
}
