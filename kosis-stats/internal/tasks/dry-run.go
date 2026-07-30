package tasks

import (
	"context"
	"encoding/json"
	"kosis/internal/pkg/dart"
	"kosis/internal/pkg/openai"
	"kosis/internal/pkg/xbrl"
	"log"
	"strings"
)

func FetchReportDryRun(dartClient *dart.DartClient, fileAnalyzer *openai.FileAnalyzer, receiptNumber string) error {
	rawDocument, err := dartClient.GetDocument(receiptNumber)
	if err == dart.ErrDocumentNotFound {
		log.Printf("document not found: %s", receiptNumber)
		return nil
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

	reportType := ""
	if strings.Contains(doc.ReportTitle, "분기보고서") || strings.Contains(doc.ReportTitle, "사업보고서") || strings.Contains(doc.ReportTitle, "반기보고서") {
		reportType = "report"
	} else {
		log.Printf("unknown report type: %s", doc.ReportTitle)
	}

	reportLength := len(j)
	var analysis interface{}
	var usedTokens int64
	ctx := context.Background()

	systemPrompt, prompt := openai.ShowPrompts(reportType, string(j))
	log.Printf("System: %s\n User: %s", systemPrompt, prompt)

	if reportLength > openai.PreviewByteLimit {
		log.Printf("analyzing report with batch API: %s", receiptNumber)
		analysis, usedTokens, err = fileAnalyzer.AnalyzeReportBatch(ctx, string(j), reportType)
		if err != nil {
			log.Printf("failed to analyze report: %v", err)
			return err
		}
	} else {
		analysis, usedTokens, err = fileAnalyzer.AnalyzeReport(ctx, string(j), reportType)
		if err != nil {
			log.Printf("failed to analyze report: %v", err)
			return err
		}
	}

	analysisJSON, err := json.MarshalIndent(analysis, "", "  ")
	if err != nil {
		log.Printf("failed to marshal analysis: %v", err)
		return err
	}

	log.Printf("analyzed report: %s, %d, %s", receiptNumber, usedTokens, string(analysisJSON))
	return nil
}
