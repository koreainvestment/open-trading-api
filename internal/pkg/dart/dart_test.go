package dart_test

import (
	"fmt"
	"kosis/internal/pkg/dart"
	"kosis/internal/testhelpers"
	"time"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("DartClient", func() {
	var client *dart.DartClient
	var apiKey = "test-dart-api-key"

	BeforeEach(func() {
		testhelpers.Activate()

		client = dart.New(apiKey)
		client.UseDefaultClient()
	})

	AfterEach(func() {
		testhelpers.Deactivate()
	})

	Describe("GetRecentRawReports", func() {
		payload := `{
			"status":"000",
			"message":"OK",
			"page_no":1,
			"total_count":1,
			"page_count":1,
			"total_page":1,
			"list":[
				{
					"rcept_no":"202500000001",
					"corp_code":"00123456",
					"corp_name":"테스트",
					"report_nm":"분기보고서 (2025.03)",
					"rcept_dt":"20250331",
					"flr_nm":"테스트",
					"rm":""
				}
			]
		}`

		It("returns list of recent reports", func() {
			startDate := time.Now().AddDate(0, 0, -5).Format("20060102")
			endDate := time.Now().Format("20060102")
			pathWithQueryString := fmt.Sprintf("/api/list.json?crtfc_key=%s&bgn_de=%s&end_de=%s&page_no=1&page_count=100", apiKey, startDate, endDate)

			testhelpers.New("https://opendart.fss.or.kr").
				Get(pathWithQueryString).
				Reply(200).
				BodyString(payload)

			list, err := client.GetRecentRawReports()
			Expect(err).NotTo(HaveOccurred())
			Expect(testhelpers.IsDone()).To(BeTrue())

			Expect(list).To(HaveLen(1))
			Expect(list[0].RceptNo).To(Equal("202500000001"))
			Expect(list[0].CorpCode).To(Equal("00123456"))
			Expect(list[0].CorpName).To(Equal("테스트"))
			Expect(list[0].ReportNm).To(Equal("분기보고서 (2025.03)"))
		})

		It("fetches the next page if there are more reports", func() {
			payload := `{
				"status":"000",
				"message":"OK",
				"page_no":1,
				"total_page":2,
				"page_count":1,
				"total_count":2,
				"list":[
					{
						"rcept_no":"202500000001",
						"corp_code":"00123456",
						"corp_name":"테스트",
						"report_nm":"분기보고서 (2025.03)",
						"rcept_dt":"20250331",
						"flr_nm":"테스트",
						"rm":""
					}
				]
			}`

			startDate := time.Now().AddDate(0, 0, -5).Format("20060102")
			endDate := time.Now().Format("20060102")
			pathWithQueryString := fmt.Sprintf("/api/list.json?crtfc_key=%s&bgn_de=%s&end_de=%s&page_no=1&page_count=100", apiKey, startDate, endDate)

			testhelpers.New("https://opendart.fss.or.kr").
				Get(pathWithQueryString).
				Reply(200).
				BodyString(payload)

			payload2 := `{
				"status":"000",
				"message":"OK",
				"page_no":2,
				"total_page":2,
				"page_count":1,
				"total_count":2,
				"list":[
					{
						"rcept_no":"202500000002",
						"corp_code":"00123457",
						"corp_name":"테스트2",
						"report_nm":"분기보고서 (2025.04)",
						"rcept_dt":"20250330",
						"flr_nm":"테스트",
						"rm":""
					}
				]
			}`

			pathWithQueryString = fmt.Sprintf("/api/list.json?crtfc_key=%s&bgn_de=%s&end_de=%s&page_no=2&page_count=100", apiKey, startDate, endDate)

			testhelpers.New("https://opendart.fss.or.kr").
				Get(pathWithQueryString).
				Reply(200).
				BodyString(payload2)

			list, err := client.GetRecentRawReports()
			Expect(err).NotTo(HaveOccurred())

			Expect(testhelpers.IsDone()).To(BeTrue())

			Expect(list).To(HaveLen(2))
		})

		It("uses custom page info if provided", func() {
			startDate := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
			endDate := time.Date(2025, 3, 1, 0, 0, 0, 0, time.UTC)
			pathWithQueryString := fmt.Sprintf("/api/list.json?crtfc_key=%s&bgn_de=%s&end_de=%s&page_no=1&page_count=100", apiKey, startDate.Format("20060102"), endDate.Format("20060102"))

			testhelpers.New("https://opendart.fss.or.kr").
				Get(pathWithQueryString).
				Reply(200).
				BodyString(payload)

			list, err := client.GetRecentRawReports(dart.PageInfo{StartDate: startDate, EndDate: endDate})
			Expect(err).NotTo(HaveOccurred())
			Expect(testhelpers.IsDone()).To(BeTrue())

			Expect(list).To(HaveLen(1))
			Expect(list[0].RceptNo).To(Equal("202500000001"))
			Expect(list[0].CorpCode).To(Equal("00123456"))
			Expect(list[0].CorpName).To(Equal("테스트"))
			Expect(list[0].ReportNm).To(Equal("분기보고서 (2025.03)"))
		})
	})
})
