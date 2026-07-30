package controllers_test

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strconv"
	"time"

	"kosis/internal/config"
	"kosis/internal/controllers"
	"kosis/internal/db"
	"kosis/internal/models"
	"kosis/internal/routes"
	"kosis/internal/testhelpers"

	"github.com/gin-gonic/gin"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"gorm.io/gorm"
)

func createCompany(dbConn *gorm.DB, ctx context.Context, company *models.Company) {
	// set default value if missing
	if company.CorpEngName == "" {
		company.CorpEngName = company.CorpName + " Eng"
	}

	if company.LastModifiedDate.IsZero() {
		company.LastModifiedDate = time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
	}

	result := gorm.WithResult()
	Expect(gorm.G[models.Company](dbConn, result).Create(ctx, company)).To(Succeed())
	Expect(result.RowsAffected).To(Equal(int64(1)))
}

func createRawReport(dbConn *gorm.DB, ctx context.Context, rawReport *models.RawReport) *models.RawReport {
	result := gorm.WithResult()
	Expect(gorm.G[models.RawReport](dbConn, result).Create(ctx, rawReport)).To(Succeed())
	Expect(result.RowsAffected).To(Equal(int64(1)))
	return rawReport
}

func createAnalysis(dbConn *gorm.DB, ctx context.Context, analysis *models.Analysis) *models.Analysis {
	result := gorm.WithResult()
	Expect(gorm.G[models.Analysis](dbConn, result).Create(ctx, analysis)).To(Succeed())
	Expect(result.RowsAffected).To(Equal(int64(1)))
	return analysis
}

var _ = Describe("FinancialController", func() {
	var (
		dbConn *gorm.DB
		router *gin.Engine
	)

	BeforeEach(func() {
		gin.SetMode(gin.TestMode)

		cfg, err := config.LoadConfig()
		Expect(err).NotTo(HaveOccurred())

		dbConn, err = db.InitDB(cfg.DatabaseURL)
		if err != nil {
			Skip("database not available: " + err.Error())
		}

		testhelpers.CleanupDB(dbConn)

		router = routes.SetupRouter(dbConn, cfg)
	})

	Describe("GET /api/v1/companies", func() {
		BeforeEach(func() {
			ctx := context.Background()

			company1 := models.Company{
				CorpCode:         "10000001",
				CorpName:         "테스트전기",
				CorpEngName:      "Electric Eng",
				LastModifiedDate: time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC),
			}
			createCompany(dbConn, ctx, &company1)

			company2 := models.Company{
				CorpCode:         "10000002",
				CorpName:         "테스트화학",
				CorpEngName:      "Chemical Eng",
				LastModifiedDate: time.Date(2025, 1, 2, 0, 0, 0, 0, time.UTC),
			}
			createCompany(dbConn, ctx, &company2)

			rawReportA := models.RawReport{
				ReceiptNumber: "20251123000001",
				CorpCode:      "10000001",
				BlobData:      []byte("doc1"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"a":1}`),
			}
			createRawReport(dbConn, ctx, &rawReportA)

			rawReportB := models.RawReport{
				ReceiptNumber: "20251123000002",
				CorpCode:      "10000002",
				BlobData:      []byte("doc2"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"b":2}`),
			}
			createRawReport(dbConn, ctx, &rawReportB)
		})

		It("returns companies", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/companies", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Companies []controllers.CompanyResponse `json:"companies"`
			}

			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.Companies).To(HaveLen(2))
		})

		It("filters companies by name", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/companies?search=화", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))
			var body struct {
				Companies []controllers.CompanyResponse `json:"companies"`
			}

			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.Companies).To(HaveLen(1))
			Expect(body.Companies[0].CorpName).To(Equal("테스트화학"))
		})

		It("filters companies by eng name", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/companies?search=Elec", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))
			var body struct {
				Companies []controllers.CompanyResponse `json:"companies"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.Companies).To(HaveLen(1))
			Expect(body.Companies[0].CorpName).To(Equal("테스트전기"))
		})
	})

	Describe("GET /api/v1/reports/:corp_code", func() {
		var (
			rawReportA models.RawReport
			rawReportB models.RawReport
		)

		BeforeEach(func() {
			ctx := context.Background()

			companyA := models.Company{
				CorpCode: "10000001",
				CorpName: "Company A",
			}
			createCompany(dbConn, ctx, &companyA)

			companyB := models.Company{
				CorpCode: "10000002",
				CorpName: "Company B",
			}
			createCompany(dbConn, ctx, &companyB)

			rawReportA = models.RawReport{
				ReceiptNumber: "20251123000001",
				CorpCode:      "10000001",
				BlobData:      []byte("doc1"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"a":1}`),
			}
			createRawReport(dbConn, ctx, &rawReportA)

			rawReportB = models.RawReport{
				ReceiptNumber: "20251123000002",
				CorpCode:      "10000002",
				BlobData:      []byte("doc2"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"b":2}`),
			}
			createRawReport(dbConn, ctx, &rawReportB)

			analysisA := models.Analysis{
				RawReportID: rawReportA.ID,
				Analysis:    json.RawMessage(`{"summary":"a"}`),
			}
			createAnalysis(dbConn, ctx, &analysisA)

			analysisB := models.Analysis{
				RawReportID: rawReportB.ID,
				Analysis:    json.RawMessage(`{"summary":"b"}`),
			}
			createAnalysis(dbConn, ctx, &analysisB)
		})

		It("returns reports for the given corp code", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports/10000001", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Reports []models.Analysis `json:"reports"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.Reports).To(HaveLen(1))
			Expect(body.Reports[0].RawReportID).To(Equal(rawReportA.ID))
		})

		It("returns error if corp code is not found", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports/10000003", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusNotFound))
			Expect(resp.Body.String()).To(MatchJSON(`{"error": "Company not found"}`))
		})
	})

	Describe("GET /api/v1/reports", func() {
		var (
			rawReportA models.RawReport
			rawReportB models.RawReport
		)

		BeforeEach(func() {
			ctx := context.Background()

			companyA := models.Company{
				CorpCode: "10000001",
				CorpName: "A 회사",
			}
			createCompany(dbConn, ctx, &companyA)

			companyB := models.Company{
				CorpCode: "10000002",
				CorpName: "B 회사",
			}
			createCompany(dbConn, ctx, &companyB)

			rawReportA = models.RawReport{
				ReceiptNumber: "20251123000001",
				ReportName:    "Report A",
				CorpCode:      "10000001",
				BlobData:      []byte("doc1"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"a":1}`),
			}
			createRawReport(dbConn, ctx, &rawReportA)

			rawReportB = models.RawReport{
				ReceiptNumber: "20251124900002",
				ReportName:    "Report B",
				CorpCode:      "10000002",
				BlobData:      []byte("doc2"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"b":2}`),
			}
			createRawReport(dbConn, ctx, &rawReportB)

			analysisA := models.Analysis{
				RawReportID: rawReportA.ID,
				Analysis:    json.RawMessage(`{"summary":"a"}`),
			}
			createAnalysis(dbConn, ctx, &analysisA)

			analysisB := models.Analysis{
				RawReportID: rawReportB.ID,
				Analysis:    json.RawMessage(`{"summary":"b"}`),
			}
			createAnalysis(dbConn, ctx, &analysisB)
		})

		It("returns all reports", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))
			Expect(resp.Body.String()).To(MatchJSON(`{
				"reports": [
					{
						"corp_name": "B 회사",
						"corp_code": "10000002",
						"report_name": "Report B",
						"raw_report_id": 2,
						"receipt_number": "20251124900002",
						"receipt_date": "2025-11-24",
						"report_type": "9",
						"analysis": {"summary": "b"}
					},
					{
						"corp_name": "A 회사",
						"corp_code": "10000001",
						"report_name": "Report A",
						"raw_report_id": 1,
						"receipt_number": "20251123000001",
						"receipt_date": "2025-11-23",
						"report_type": "0",
						"analysis": {"summary": "a"}
					}
				]
			}`))
		})

		It("filters reports by corp name", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports?corp_code=10000001", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)
			Expect(resp.Code).To(Equal(http.StatusOK))
			Expect(resp.Body.String()).To(MatchJSON(`{
				"reports": [
					{
						"corp_name": "A 회사",
						"corp_code": "10000001",
						"report_name": "Report A",
						"raw_report_id": 1,
						"receipt_number": "20251123000001",
						"receipt_date": "2025-11-23",
						"report_type": "0",
						"analysis": {"summary": "a"}
					}
				]
			}`))
		})

		It("filters reports by date", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports?start_date=2025-11-23&end_date=2025-11-24", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)
			Expect(resp.Code).To(Equal(http.StatusOK))
			Expect(resp.Body.String()).To(MatchJSON(`{
				"reports": [
					{
						"corp_name": "A 회사",
						"corp_code": "10000001",
						"report_name": "Report A",
						"raw_report_id": 1,
						"receipt_number": "20251123000001",
						"receipt_date": "2025-11-23",
						"report_type": "0",
						"analysis": {"summary": "a"}
					}
				]
			}`))
		})

		It("sets end_date to the next day if it's the same as start_date", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports?start_date=2025-11-23&end_date=2025-11-23", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)
			Expect(resp.Code).To(Equal(http.StatusOK))
			Expect(resp.Body.String()).To(MatchJSON(`{
				"reports": [
					{
						"corp_name": "A 회사",
						"corp_code": "10000001",
						"report_name": "Report A",
						"raw_report_id": 1,
						"receipt_number": "20251123000001",
						"receipt_date": "2025-11-23",
						"report_type": "0",
						"analysis": {"summary": "a"}
					}
				]
			}`))
		})
	})

	Describe("GET /api/v1/reports/:corp_code/:raw_report_id", func() {
		It("returns raw report for the given corp code and raw report id", func() {
			rawReportA := models.RawReport{
				ReceiptNumber: "20251123000001",
				CorpCode:      "10000001",
				BlobData:      []byte("doc1"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"a":1}`),
			}

			ctx := context.Background()
			createRawReport(dbConn, ctx, &rawReportA)

			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports/10000001/"+strconv.FormatUint(uint64(rawReportA.ID), 10), nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)
			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				RawReport string `json:"raw_report"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.RawReport).To(Equal(base64.StdEncoding.EncodeToString([]byte("doc1"))))
		})
	})

	Describe("GET /api/v1/reports/receipt/:receipt_number", func() {
		receiptNumber := "20251123000001"
		var rawReport *models.RawReport

		BeforeEach(func() {
			ctx := context.Background()
			rawReport = &models.RawReport{
				ReceiptNumber: receiptNumber,
				CorpCode:      "10000001",
				ReportName:    "Report A",
				BlobData:      []byte("doc1"),
				BlobSize:      4,
				JSONData:      json.RawMessage(`{"a":1}`),
			}
			createRawReport(dbConn, ctx, rawReport)

			analysis := &models.Analysis{
				RawReportID: rawReport.ID,
				Analysis:    json.RawMessage(`{"summary":"a"}`),
			}
			createAnalysis(dbConn, ctx, analysis)
		})

		It("returns summary and raw report for the given receipt number", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports/receipt/"+receiptNumber, nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)
			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Summary   json.RawMessage `json:"summary"`
				RawReport string          `json:"raw_report"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(string(body.Summary)).To(MatchJSON(`{"summary":"a"}`))
			Expect(body.RawReport).To(Equal(base64.StdEncoding.EncodeToString([]byte("doc1"))))
		})

		It("returns 404 if receipt number is not found", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/reports/receipt/20251123099999", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusNotFound))
			Expect(resp.Body.String()).To(MatchJSON(`{"error": "Raw report not found"}`))
		})
	})

	Describe("GET /api/v1/mcp/reports/by-corp-name", func() {
		BeforeEach(func() {
			ctx := context.Background()

			company1 := models.Company{
				CorpCode: "20000001",
				CorpName: "Alpha Corp",
			}
			createCompany(dbConn, ctx, &company1)

			company2 := models.Company{
				CorpCode: "20000002",
				CorpName: "Alpha Industries",
			}
			createCompany(dbConn, ctx, &company2)

			company3 := models.Company{
				CorpCode: "20000003",
				CorpName: "Beta Ltd",
			}
			createCompany(dbConn, ctx, &company3)

			// Create reports for Alpha Corp
			rawReportA := createRawReport(dbConn, ctx, &models.RawReport{
				ReceiptNumber: "20251123000100",
				CorpCode:      "20000001",
				BlobData:      []byte("data"),
				JSONData:      json.RawMessage(`{}`),
			})

			rawReportB := createRawReport(dbConn, ctx, &models.RawReport{
				ReceiptNumber: "20251123000101",
				CorpCode:      "20000001",
				BlobData:      []byte("data"),
				JSONData:      json.RawMessage(`{}`),
			})

			// Create report for Alpha Industries
			rawReportC := createRawReport(dbConn, ctx, &models.RawReport{
				ReceiptNumber: "20251123000200",
				CorpCode:      "20000002",
				BlobData:      []byte("data"),
				JSONData:      json.RawMessage(`{}`),
			})

			// Create report for Beta Ltd
			rawReportD := createRawReport(dbConn, ctx, &models.RawReport{
				ReceiptNumber: "20251123000300",
				CorpCode:      "20000003",
				BlobData:      []byte("data"),
				JSONData:      json.RawMessage(`{}`),
			})

			createAnalysis(dbConn, ctx, &models.Analysis{
				RawReportID: rawReportA.ID,
				Analysis:    json.RawMessage(`{"summary":"a"}`),
			})

			createAnalysis(dbConn, ctx, &models.Analysis{
				RawReportID: rawReportB.ID,
				Analysis:    json.RawMessage(`{"summary":"b"}`),
			})

			createAnalysis(dbConn, ctx, &models.Analysis{
				RawReportID: rawReportC.ID,
				Analysis:    json.RawMessage(`{"summary":"c"}`),
			})

			createAnalysis(dbConn, ctx, &models.Analysis{
				RawReportID: rawReportD.ID,
				Analysis:    json.RawMessage(`{"summary":"d"}`),
			})
		})

		It("returns reports matching the corp name partially", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/mcp/reports/by-corp-name?corp_name=Alpha", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Reports []models.RawReport `json:"reports"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())

			// Alpha Corp (2) + Alpha Industries (1) = 3
			Expect(body.Reports).To(HaveLen(3))
		})

		It("returns 400 if corp_name is missing", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/mcp/reports/by-corp-name", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusBadRequest))
		})

		It("respects the limit parameter", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/mcp/reports/by-corp-name?corp_name=Alpha&limit=2", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Reports []models.RawReport `json:"reports"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(body.Reports).To(HaveLen(2))
		})

		It("prevents negative limit parameter (DoS vulnerability)", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/mcp/reports/by-corp-name?corp_name=Alpha&limit=-1", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Reports []models.RawReport `json:"reports"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(len(body.Reports)).To(BeNumerically("<=", 10)) // Should fall back to default limit
		})

		It("caps excessively large limit parameters", func() {
			req := httptest.NewRequest(http.MethodGet, "/api/v1/mcp/reports/by-corp-name?corp_name=Alpha&limit=1000", nil)
			resp := httptest.NewRecorder()

			router.ServeHTTP(resp, req)

			Expect(resp.Code).To(Equal(http.StatusOK))

			var body struct {
				Reports []models.RawReport `json:"reports"`
			}
			Expect(json.Unmarshal(resp.Body.Bytes(), &body)).To(Succeed())
			Expect(len(body.Reports)).To(BeNumerically("<=", 100)) // Capped at 100
		})
	})
})
