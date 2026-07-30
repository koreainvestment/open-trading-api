package openai

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	openai "github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/option"
	"github.com/openai/openai-go/v3/responses"
	"github.com/openai/openai-go/v3/shared"
)

type CorrectionReportJSON struct {
	DocID   string `json:"doc_id"`
	DocType string `json:"doc_type"`
	Issuer  struct {
		Name    string `json:"name"`
		AregCIK string `json:"areg_cik"`
	} `json:"issuer"`
	Dates struct {
		FirstFiled          string `json:"first_filed"`
		CorrectionAnnounced string `json:"correction_announced"`
	} `json:"dates"`
	Tranches []struct {
		Name      string `json:"name"`
		Seniority string `json:"seniority"`
		AmountKRW int64  `json:"amount_krw"`
	} `json:"tranches"`
	Totals struct {
		AmountKRW              int64   `json:"amount_krw"`
		WACBeforePCT           float64 `json:"wac_before_pct"`
		WACAfterPCT            float64 `json:"wac_after_pct"`
		WACDeltaBp             int64   `json:"wac_delta_bp"`
		AnnualInterestDeltaKRW int64   `json:"annual_interest_delta_krw"`
	} `json:"totals"`
	ReasonOfCorrection string  `json:"reason_of_correction"`
	SpreadAfterBp      float64 `json:"spread_after_bp"`
	ImpactScore        struct {
		EquityImpact0to5    float64 `json:"equity_impact_0to5"`
		CreditImpact0to5    float64 `json:"credit_impact_0to5"`
		LiquidityImpact0to5 float64 `json:"liquidity_impact_0to5"`
	} `json:"impact_score"`
	Notes string `json:"notes"`
}

type Score struct {
	Direction      string   `json:"direction"`  // down, up
	Magnitude      float64  `json:"magnitude"`  // 0-100
	Confidence     float64  `json:"confidence"` // 0.0-1.0
	Horizons       []string `json:"horizons"`   // "ST"
	RationaleShort string   `json:"rationale_short"`
}

type SupplyExtract struct {
	DocID     string `json:"doc_id"`
	CorpName  string `json:"corp_name"`
	Title     string `json:"report_title"`
	EventCode string `json:"event_code"` // "SUPPLY"
	Amendment struct {
		Reason         string  `json:"reason"`
		PrevAmountKRW  int64   `json:"prev_amount_krw"`
		NewAmountKRW   int64   `json:"new_amount_krw"`
		PrevRatioSales float64 `json:"prev_ratio_to_sales"`
		NewRatioSales  float64 `json:"new_ratio_to_sales"`
	} `json:"amendment"`
	Contract struct {
		Name                  string  `json:"name"`
		Counterparty          string  `json:"counterparty"`
		AmountKRW             int64   `json:"amount_krw"`
		CompanyRecentSalesKRW int64   `json:"company_recent_sales_krw"`
		CounterpartySalesKRW  int64   `json:"counterparty_recent_sales_krw"`
		Country               string  `json:"country"`
		TermFrom              string  `json:"term_from"` // YYYY-MM-DD
		TermTo                string  `json:"term_to"`   // YYYY-MM-DD
		ProgressPct           float64 `json:"progress_pct"`
	} `json:"contract"`
	Score Score `json:"score"`
}

type IssuanceTermsExtract struct {
	DocID  string `json:"doc_id"`
	Issuer struct {
		Name    string `json:"name"`
		AregCik string `json:"areg_cik"`
	} `json:"issuer"`
	EventCode string `json:"event_code"` // "SECURITY_ISSUANCE_TERMS"
	Tranches  []struct {
		Name            string  `json:"name"`
		Seniority       string  `json:"seniority"` // "senior"|"subordinated"|null
		AmountKRW       int64   `json:"amount_krw"`
		CouponBeforePct float64 `json:"coupon_before_pct"`
		CouponAfterPct  float64 `json:"coupon_after_pct"`
		CouponDeltaBp   float64 `json:"coupon_delta_bp"`
	} `json:"tranches"`
	Totals struct {
		AmountKRW    int64   `json:"amount_krw"`
		WacBeforePct float64 `json:"wac_before_pct"`
		WacAfterPct  float64 `json:"wac_after_pct"`
		WacDeltaBp   float64 `json:"wac_delta_bp"`
	} `json:"totals"`
	ReasonOfCorrection string   `json:"reason_of_correction"`
	SpreadAfterBp      float64  `json:"spread_after_bp"`
	Notes              []string `json:"notes"`
	Score              Score    `json:"score"`
}

type batchRequest struct {
	CustomID string                      `json:"custom_id"`
	Method   string                      `json:"method"`
	URL      string                      `json:"url"`
	Body     responses.ResponseNewParams `json:"body"`
}

type batchOutputLine struct {
	CustomID string `json:"custom_id"`
	Error    *struct {
		Message string `json:"message"`
		Code    string `json:"code"`
		Type    string `json:"type"`
		Param   string `json:"param"`
	} `json:"error"`
	Response struct {
		StatusCode int             `json:"status_code"`
		Body       json.RawMessage `json:"body"`
	} `json:"response"`
}

// FileAnalyzer is a thin wrapper around the OpenAI responses client that can
// analyze a local file using the latest SDK.
type FileAnalyzer struct {
	client *openai.Client
	model  shared.ResponsesModel
}

const (
	defaultModel     = shared.ResponsesModel("gpt-5.2")
	PreviewByteLimit = 128 * 1024 // cap what we send to the model, 128KB
)

var (
	// ErrMissingAPIKey is returned when OPENAI_API_KEY was not configured.
	ErrMissingAPIKey = errors.New("OPENAI_API_KEY is not set")
)

// NewFileAnalyzerFromEnv builds a FileAnalyzer using the OPENAI_API_KEY env var.
func NewFileAnalyzerFromEnv() (*FileAnalyzer, error) {
	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		return nil, ErrMissingAPIKey
	}

	client := openai.NewClient(option.WithAPIKey(apiKey))
	return &FileAnalyzer{client: &client, model: defaultModel}, nil
}

func NewFileAnalyzer(apiKey string, model ...shared.ResponsesModel) *FileAnalyzer {
	client := openai.NewClient(option.WithAPIKey(apiKey))
	if len(model) > 0 {
		return &FileAnalyzer{client: &client, model: model[0]}
	}

	return &FileAnalyzer{client: &client, model: defaultModel}
}

// AnalyzeFile sends the file contents to the OpenAI Responses API and returns the
// assistant's answer for the provided question.
func (a *FileAnalyzer) AnalyzeFile(ctx context.Context, filePath string, docType string) (interface{}, error) {
	if a == nil || a.client == nil {
		return nil, errors.New("FileAnalyzer is not initialized")
	}

	contents, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("read %s: %w", filePath, err)
	}

	mainPrompt, prompt, report := preparePrompt(docType, string(contents), true)

	resp, err := a.client.Responses.New(ctx, responses.ResponseNewParams{
		Model: a.model,
		Input: responses.ResponseNewParamsInputUnion{
			OfInputItemList: responses.ResponseInputParam{
				responses.ResponseInputItemParamOfMessage(mainPrompt, responses.EasyInputMessageRoleSystem),
				responses.ResponseInputItemParamOfMessage(prompt, responses.EasyInputMessageRoleUser),
			},
		},
		ServiceTier: responses.ResponseNewParamsServiceTierFlex,
		//		Reasoning: shared.ReasoningParam{
		//			Effort:  shared.ReasoningEffortHigh,
		//			Summary: shared.ReasoningSummaryDetailed,
		//		},
	})

	if err != nil {
		return nil, fmt.Errorf("call OpenAI: %w", err)
	}

	output := strings.TrimSpace(resp.OutputText())
	if output == "" {
		return nil, errors.New("model returned an empty response")
	}

	if err := json.Unmarshal([]byte(output), report); err != nil {
		return nil, fmt.Errorf("unmarshal JSON: %w", err)
	}

	if docType == "report" {
		metrics := analyzeTrends(report.(*Report))
		log.Printf("Trend Metrics: %+v\n", metrics)
	}

	return report, nil
}

func (a *FileAnalyzer) AnalyzeReport(ctx context.Context, contents string, docType string) (interface{}, int64, error) {
	mainPrompt, prompt, report := preparePrompt(docType, contents, true)

	resp, err := a.client.Responses.New(ctx, responses.ResponseNewParams{
		Model: a.model,
		Input: responses.ResponseNewParamsInputUnion{
			OfInputItemList: responses.ResponseInputParam{
				responses.ResponseInputItemParamOfMessage(mainPrompt, responses.EasyInputMessageRoleSystem),
				responses.ResponseInputItemParamOfMessage(prompt, responses.EasyInputMessageRoleUser),
			},
		},
	})

	if err != nil {
		return nil, 0, fmt.Errorf("call OpenAI: %w", err)
	}

	log.Printf("resp: %s, input: %d, output: %d, total: %d\n", resp.ID, resp.Usage.InputTokens, resp.Usage.OutputTokens, resp.Usage.TotalTokens)

	output := strings.TrimSpace(resp.OutputText())
	if output == "" {
		return nil, 0, errors.New("model returned an empty response")
	}

	if err := json.Unmarshal([]byte(output), report); err != nil {
		return nil, 0, fmt.Errorf("unmarshal JSON: %w", err)
	}

	// if docType == "report" {
	// 	metrics := analyzeTrends(report.(*Report))
	// 	log.Printf("Trend Metrics: %+v\n", metrics)
	// }

	return report, resp.Usage.TotalTokens, nil
}

func (a *FileAnalyzer) GetModel() shared.ResponsesModel {
	return a.model
}

// AnalyzeReportBatch uses the Batch API to handle large inputs without truncation.
// This keeps the original AnalyzeReport behavior unchanged and opt-in.
func (a *FileAnalyzer) AnalyzeReportBatch(ctx context.Context, contents string, docType string) (interface{}, int64, error) {
	return a.analyzeReportWithBatch(ctx, contents, docType)
}

func (a *FileAnalyzer) analyzeReportWithBatch(ctx context.Context, contents string, docType string) (interface{}, int64, error) {
	mainPrompt, prompt, report := preparePrompt(docType, contents, false)

	linePayload := batchRequest{
		CustomID: fmt.Sprintf("report-%d", time.Now().UnixNano()),
		Method:   http.MethodPost,
		URL:      "/v1/responses",
		Body: responses.ResponseNewParams{
			Model: a.model,
			Input: responses.ResponseNewParamsInputUnion{
				OfInputItemList: responses.ResponseInputParam{
					responses.ResponseInputItemParamOfMessage(mainPrompt, responses.EasyInputMessageRoleSystem),
					responses.ResponseInputItemParamOfMessage(prompt, responses.EasyInputMessageRoleUser),
				},
			},
		},
	}

	lineBytes, err := json.Marshal(linePayload)
	if err != nil {
		return nil, 0, fmt.Errorf("marshal batch request: %w", err)
	}

	tmpFile, err := os.CreateTemp("", "xbrl-batch-*.jsonl")
	if err != nil {
		return nil, 0, fmt.Errorf("create temp batch file: %w", err)
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.Write(append(lineBytes, '\n')); err != nil {
		return nil, 0, fmt.Errorf("write batch file: %w", err)
	}
	if err := tmpFile.Close(); err != nil {
		return nil, 0, fmt.Errorf("close batch file: %w", err)
	}

	f, err := os.Open(tmpFile.Name())
	if err != nil {
		return nil, 0, fmt.Errorf("open batch file: %w", err)
	}
	defer f.Close()

	upload, err := a.client.Files.New(ctx, openai.FileNewParams{
		File:    f,
		Purpose: openai.FilePurposeBatch,
	})
	if err != nil {
		return nil, 0, fmt.Errorf("upload batch input: %w", err)
	}

	batch, err := a.client.Batches.New(ctx, openai.BatchNewParams{
		CompletionWindow: openai.BatchNewParamsCompletionWindow24h,
		Endpoint:         openai.BatchNewParamsEndpointV1Responses,
		InputFileID:      upload.ID,
	})
	if err != nil {
		return nil, 0, fmt.Errorf("create batch: %w", err)
	}

	completedBatch, err := a.waitForBatchCompletion(ctx, batch.ID)
	if err != nil {
		return nil, 0, err
	}
	log.Printf("batch: %s, input: %d, output: %d, total: %d\n", completedBatch.ID, completedBatch.Usage.InputTokens, completedBatch.Usage.OutputTokens, completedBatch.Usage.TotalTokens)

	if completedBatch.OutputFileID == "" {
		return nil, 0, errors.New("batch completed without output file")
	}

	outputResp, err := a.client.Files.Content(ctx, completedBatch.OutputFileID)
	if err != nil {
		return nil, 0, fmt.Errorf("download batch output: %w", err)
	}
	defer outputResp.Body.Close()

	outputData, err := io.ReadAll(outputResp.Body)
	if err != nil {
		return nil, 0, fmt.Errorf("read batch output: %w", err)
	}

	return parseBatchOutput(outputData, report)
}

func (a *FileAnalyzer) waitForBatchCompletion(ctx context.Context, batchID string) (*openai.Batch, error) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-ticker.C:
			current, err := a.client.Batches.Get(ctx, batchID)
			if err != nil {
				return nil, fmt.Errorf("poll batch %s: %w", batchID, err)
			}

			log.Printf("batch %s status: %s", batchID, current.Status)

			switch current.Status {
			case openai.BatchStatusCompleted:
				return current, nil
			case openai.BatchStatusFailed, openai.BatchStatusCancelled, openai.BatchStatusExpired:
				return nil, fmt.Errorf("batch %s ended with status %s: %+v", batchID, current.Status, current.Errors)
			}
		}
	}
}

func parseBatchOutput(raw []byte, report interface{}) (interface{}, int64, error) {
	scanner := bufio.NewScanner(bytes.NewReader(raw))
	// Allow scanning large JSONL lines.
	scanner.Buffer(make([]byte, 0, 1024*1024), 32*1024*1024)

	for scanner.Scan() {
		line := bytes.TrimSpace(scanner.Bytes())
		if len(line) == 0 {
			continue
		}

		var payload batchOutputLine
		if err := json.Unmarshal(line, &payload); err != nil {
			return nil, 0, fmt.Errorf("unmarshal batch output line: %w", err)
		}

		if payload.Error != nil {
			return nil, 0, fmt.Errorf("batch item error: %s", payload.Error.Message)
		}

		if payload.Response.StatusCode != http.StatusOK {
			return nil, 0, fmt.Errorf("batch response returned status %d", payload.Response.StatusCode)
		}

		var resp responses.Response
		if err := json.Unmarshal(payload.Response.Body, &resp); err != nil {
			return nil, 0, fmt.Errorf("unmarshal response body: %w", err)
		}

		output := strings.TrimSpace(resp.OutputText())
		if output == "" {
			return nil, 0, errors.New("model returned an empty response")
		}

		if err := json.Unmarshal([]byte(output), report); err != nil {
			return nil, 0, fmt.Errorf("unmarshal JSON: %w", err)
		}

		return report, resp.Usage.TotalTokens, nil
	}

	if err := scanner.Err(); err != nil {
		return nil, 0, fmt.Errorf("scan batch output: %w", err)
	}

	return nil, 0, errors.New("no batch output lines found")
}

func ShowPrompts(docType string, contents string) (string, string) {
	systemPrompt, prompt, _ := preparePrompt(docType, contents, false)
	return systemPrompt, prompt
}

func preparePrompt(docType string, contents string, truncate bool) (string, string, interface{}) {
	mainPrompt := systemPrompt
	additionalPrompt := ""
	var report interface{}

	switch docType {
	case "securities_issuance_terms":
		mainPrompt += securitiesIssuanceTermsSchema
		additionalPrompt = additionalSecuritiesIssuanceTermsSchema
		report = &CorrectionReportJSON{}
	case "supply":
		mainPrompt += supplySchema
		report = &SupplyExtract{}
	case "report":
		mainPrompt += reportSchema
		additionalPrompt = additionalReportSchema
		report = &Report{}
	default:
		mainPrompt += fmt.Sprintf("\n%s", defaultSchema)
		additionalPrompt = fmt.Sprintf("\n%s", defaultAdditionalSchema)
		report = &DefaultReport{}
	}

	prompt := buildPromptWithLimit(contents, additionalPrompt, truncate)
	return mainPrompt, prompt, report
}

func buildPromptWithLimit(rawContents string, additionalPrompt string, enforceLimit bool) string {
	if enforceLimit && len(rawContents) > PreviewByteLimit {
		rawContents = rawContents[:PreviewByteLimit] + "\n\n[...truncated for brevity...]"
	}

	builder := strings.Builder{}
	builder.WriteString("다음은 DART 공시 원문이다. 필요한 정보를 추출해 스키마에 맞춰 JSON만 출력하라.")
	builder.WriteString("공시 원문:\n")
	builder.WriteString(rawContents)
	builder.WriteString("\n\n")
	builder.WriteString(`추가 지시: `)
	builder.WriteString(additionalPrompt)

	return builder.String()
}
