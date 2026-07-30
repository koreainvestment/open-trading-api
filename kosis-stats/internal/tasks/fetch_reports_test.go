package tasks_test

import (
	"context"
	"encoding/json"
	"fmt"
	"kosis/internal/config"
	"kosis/internal/db"
	"kosis/internal/models"
	"kosis/internal/pkg/openai"
	"kosis/internal/tasks"
	"kosis/internal/testhelpers"
	"strings"

	"github.com/hibiken/asynq"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"gorm.io/gorm"
)

var _ = Describe("HandleFetchReportsTask", func() {
	var dbConn *gorm.DB
	var p *tasks.TaskProcessor
	var listWithOneReport = `{
		"status": "000",
		"message": "정상",
		"page_no": 1,
		"page_count": 1,
		"total_count": 1,
		"total_page": 1,
		"list": [
			{
				"corp_code": "00356361",
				"corp_name": "LG화학",
				"stock_code": "051910",
				"corp_cls": "Y",
				"report_nm": "분기보고서 (2025.09)",
				"rcept_no": "20251114001374",
				"flr_nm": "LG화학",
				"rcept_dt": "20251114",
				"rm": ""
			}
		]
	}`

	var errRes1 = `{ "status": "014", "message": "문서가 존재하지 않습니다." }`
	var errRes2 = `{ "status": "010","message":"등록되지 않은 인증키입니다." }`
	var errRes3 = `{ "status": "013","message":"등록된 종목코드 또는 고유번호가 아닙니다." }`

	var testDocument = `<DOCUMENT>
  <DOCUMENT-NAME>Form 10-K</DOCUMENT-NAME>
  <COMPANY-NAME AREGCIK="00001234">ACME Corp</COMPANY-NAME>
  <TABLE>
    <TR>
      <TH>Metric</TH>
      <TH>Amount</TH>
    </TR>
    <TR>
      <TD><span>Revenue</span></TD>
      <TD><span>1000</span></TD>
    </TR>
    <TR>
      <TU>Profit</TU>
      <TE>500</TE>
    </TR>
  </TABLE>
  <TABLE>
    <TR>
      <TD>Line Item</TD>
      <TD>Value</TD>
    </TR>
    <TR>
      <TD>Total Assets</TD>
      <TD>2000</TD>
    </TR>
  </TABLE>
  <P> Primary discussion. </P>
  <P>    </P>
  <P>Secondary paragraph</P>
</DOCUMENT>`

	var openaiResFmt = `{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
      		"text": "%s",
      		"annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}`

	BeforeEach(func() {
		cfg, err := config.LoadConfig()
		Expect(err).NotTo(HaveOccurred())

		dbConn, err = db.InitDB(cfg.DatabaseURL)
		Expect(err).NotTo(HaveOccurred())

		testhelpers.CleanupDB(dbConn)

		p = tasks.NewTaskProcessor(dbConn, cfg)

		testhelpers.Activate()
		p.GetDartClient().UseDefaultClient()
	})

	AfterEach(func() {
		testhelpers.Deactivate()
	})

	It("stores raw reports", func() {
		testhelpers.New("https://opendart.fss.or.kr").
			Get("/api/list.json").Reply(200).
			BodyString(listWithOneReport).
			Header("Content-Type", "application/json")

		zipDocument, err := testhelpers.CreateMockZipArchive("document.xml", []byte(testDocument))
		Expect(err).NotTo(HaveOccurred())

		testhelpers.New("https://opendart.fss.or.kr").Get("/api/document.xml").Reply(200).Body(zipDocument).Header("Content-Type", "application/zip").Header("Content-Disposition", `attachment; filename="document.zip"`)

		rawData := `{ \"company_name\": \"LG화학\", \"date\": \"2025-09-30\", \"type\": \"report\", \"summary\": \"LG화학의 2025년 3분기 보고서\" }`
		testhelpers.New("https://api.openai.com").
			Post("/v1/responses").Reply(200).
			BodyString(fmt.Sprintf(openaiResFmt, rawData)).
			Header("Content-Type", "application/json")

		ctx := context.Background()
		err = p.HandleFetchReportsTask(ctx, asynq.NewTask(tasks.TypeTaskFetchReports, []byte("{}")))
		Expect(err).NotTo(HaveOccurred())

		result, err := gorm.G[models.RawReport](dbConn).Where("corp_code = ?", "00356361").First(ctx)
		Expect(err).NotTo(HaveOccurred())
		Expect(result.ReceiptNumber).To(Equal("20251114001374"))
		Expect(result.CorpCode).To(Equal("00356361"))
		Expect(result.ReportName).To(Equal("분기보고서 (2025.09)"))
		Expect(strings.TrimSpace(string(result.BlobData))).To(Equal(strings.TrimSpace(testDocument)))
		Expect(result.JSONData).To(MatchJSON(`{"company_name": "ACME Corp", "report_title": "Form 10-K", "company_cik": "00001234", "tables": [[["Metric", "Amount"], ["Revenue", "1000"], ["Profit", "500"]], [["Line Item", "Value"], ["Total Assets", "2000"]]], "key_paragraphs": ["Primary discussion.", "Secondary paragraph"]}`))

		analysis, err := gorm.G[models.Analysis](dbConn).Where("raw_report_id = ?", result.ID).First(ctx)
		Expect(err).NotTo(HaveOccurred())

		Expect(analysis.UsedTokens).To(Equal(int64(123)))
		var analysisData map[string]interface{}
		Expect(json.Unmarshal(analysis.Analysis, &analysisData)).NotTo(HaveOccurred())
		Expect(analysisData["company_name"]).To(Equal("LG화학"))
		Expect(analysisData["date"]).To(Equal("2025-09-30"))
		Expect(analysisData["type"]).To(Equal("report"))
		Expect(analysisData["summary"]).To(Equal("LG화학의 2025년 3분기 보고서"))
	})

	It("sets company name if not set", func() {
		testhelpers.New("https://opendart.fss.or.kr").
			Get("/api/list.json").Reply(200).
			BodyString(listWithOneReport).
			Header("Content-Type", "application/json")

		zipDocument, err := testhelpers.CreateMockZipArchive("document.xml", []byte(testDocument))
		Expect(err).NotTo(HaveOccurred())

		testhelpers.New("https://opendart.fss.or.kr").Get("/api/document.xml").Reply(200).Body(zipDocument).Header("Content-Type", "application/zip").Header("Content-Disposition", `attachment; filename="document.zip"`)

		company := models.Company{
			CorpCode: "00356361",
			CorpName: "LG화학",
		}

		ctx := context.Background()
		dbResult := gorm.WithResult()
		err = gorm.G[models.Company](dbConn, dbResult).Create(ctx, &company)
		Expect(err).NotTo(HaveOccurred())
		Expect(dbResult.RowsAffected).To(Equal(int64(1)))

		rawData := `{ \"company_name\": \"\", \"date\": \"2025-09-30\", \"type\": \"report\", \"summary\": \"LG화학의 2025년 3분기 보고서\" }`
		testhelpers.New("https://api.openai.com").
			Post("/v1/responses").Reply(200).
			BodyString(fmt.Sprintf(openaiResFmt, rawData)).
			Header("Content-Type", "application/json")

		err = p.HandleFetchReportsTask(ctx, asynq.NewTask(tasks.TypeTaskFetchReports, []byte("{}")))
		Expect(err).NotTo(HaveOccurred())

		result, err := gorm.G[models.RawReport](dbConn).Where("corp_code = ?", "00356361").First(ctx)
		Expect(err).NotTo(HaveOccurred())
		Expect(result.ReceiptNumber).To(Equal("20251114001374"))
		Expect(result.CorpCode).To(Equal("00356361"))
		Expect(strings.TrimSpace(string(result.BlobData))).To(Equal(strings.TrimSpace(testDocument)))
		Expect(result.JSONData).To(MatchJSON(`{"company_name": "ACME Corp", "report_title": "Form 10-K", "company_cik": "00001234", "tables": [[["Metric", "Amount"], ["Revenue", "1000"], ["Profit", "500"]], [["Line Item", "Value"], ["Total Assets", "2000"]]], "key_paragraphs": ["Primary discussion.", "Secondary paragraph"]}`))

		analysis, err := gorm.G[models.Analysis](dbConn).Where("raw_report_id = ?", result.ID).First(ctx)
		Expect(err).NotTo(HaveOccurred())
		var analysisData map[string]interface{}
		Expect(json.Unmarshal(analysis.Analysis, &analysisData)).NotTo(HaveOccurred())
		Expect(analysisData["company_name"]).To(Equal("LG화학"))
		Expect(analysisData["date"]).To(Equal("2025-09-30"))
		Expect(analysisData["type"]).To(Equal("report"))
		Expect(analysisData["summary"]).To(Equal("LG화학의 2025년 3분기 보고서"))
	})

	It("skips if raw report already exists", func() {
		testhelpers.New("https://opendart.fss.or.kr").
			Get("/api/list.json").Reply(200).BodyString(listWithOneReport).Header("Content-Type", "application/json")

		rawReport := models.RawReport{
			ReceiptNumber: "20251114001374",
			CorpCode:      "00356361",
			BlobData:      []byte("<DOCUMENT><CONTENT><TEXT><P>Hello, world!</P></TEXT></CONTENT></DOCUMENT>"),
			BlobSize:      41,
			JSONData:      []byte(`{"company_name": "hello"}`),
		}

		ctx := context.Background()
		result := gorm.WithResult()

		err := gorm.G[models.RawReport](dbConn, result).Create(ctx, &rawReport)
		Expect(err).NotTo(HaveOccurred())

		err = p.HandleFetchReportsTask(ctx, asynq.NewTask(tasks.TypeTaskFetchReports, []byte("{}")))
		Expect(err).NotTo(HaveOccurred())
	})

	DescribeTable("Handle errors from Dart API",
		func(bodyString string) {
			testhelpers.New("https://opendart.fss.or.kr").
				Get("/api/list.json").Reply(200).BodyString(bodyString)

			ctx := context.Background()
			err := p.HandleFetchReportsTask(ctx, asynq.NewTask(tasks.TypeTaskFetchReports, []byte("{}")))
			Expect(err).NotTo(HaveOccurred())

			count, err := gorm.G[models.RawReport](dbConn).Count(ctx, "id")
			Expect(err).NotTo(HaveOccurred())
			Expect(count).To(BeZero())
		},
		Entry("document not found", errRes1),
		Entry("invalid API key", errRes2),
		Entry("invalid corp code", errRes3),
	)
})

var _ = Describe("AnalyzeReportBatch", func() {
	BeforeEach(func() {
		testhelpers.Activate()
	})

	AfterEach(func() {
		testhelpers.Deactivate()
	})

	It("parses batch output without truncation", func() {
		analyzer := openai.NewFileAnalyzer("dummy-key")
		openaiResFmtBatch := `{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
      		"text": "%s",
      		"annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}`

		// Mock file upload for batch input
		testhelpers.New("https://api.openai.com").
			Post("/v1/files").
			Reply(200).
			BodyString(`{"id":"file-123","bytes":10,"created_at":1,"filename":"batch.jsonl","object":"file","purpose":"batch","status":"processed"}`).
			Header("Content-Type", "application/json")

		// Mock batch creation
		testhelpers.New("https://api.openai.com").
			Post("/v1/batches").
			Reply(200).
			BodyString(`{"id":"batch-123","completion_window":"24h","created_at":1,"endpoint":"/v1/responses","input_file_id":"file-123","object":"batch","status":"validating"}`).
			Header("Content-Type", "application/json")

		// Mock batch polling to completed state
		testhelpers.New("https://api.openai.com").
			Get("/v1/batches/batch-123").
			Reply(200).
			BodyString(`{"id":"batch-123","completion_window":"24h","created_at":1,"endpoint":"/v1/responses","input_file_id":"file-123","object":"batch","status":"completed","output_file_id":"file-out-123"}`).
			Header("Content-Type", "application/json")

		rawData := `{ \"company_name\": \"ACME\", \"period_end_date\": \"2025-09-30\", \"period_start_date\": \"2025-07-01\", \"submission_date\": \"2025-11-14\" }`
		batchResponse := fmt.Sprintf(strings.ReplaceAll(openaiResFmtBatch, "\n", ""), rawData)
		batchOutputLine := fmt.Sprintf(`{"custom_id":"report-1","response":{"status_code":200,"body":%s}}`, batchResponse)

		testhelpers.New("https://api.openai.com").
			Get("/v1/files/file-out-123/content").
			Reply(200).
			BodyString(batchOutputLine+"\n").
			Header("Content-Type", "application/x-ndjson")

		ctx := context.Background()
		result, tokens, err := analyzer.AnalyzeReportBatch(ctx, strings.Repeat("X", 130000), "report")
		Expect(err).NotTo(HaveOccurred())

		report, ok := result.(*openai.Report)
		Expect(ok).To(BeTrue())
		Expect(report.CompanyName).To(Equal("ACME"))
		Expect(report.PeriodEnd).To(Equal("2025-09-30"))
		Expect(report.PeriodStart).To(Equal("2025-07-01"))
		Expect(report.SubmissionDate).To(Equal("2025-11-14"))
		Expect(tokens).To(Equal(int64(123)))
	})
})
