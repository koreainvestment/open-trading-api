package tasks_test

import (
	"context"
	"kosis/internal/config"
	"kosis/internal/db"
	"kosis/internal/models"
	"kosis/internal/tasks"
	"kosis/internal/testhelpers"
	"time"

	"github.com/hibiken/asynq"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
	"gorm.io/gorm"
)

var _ = Describe("HandleFetchCompaniesTask", func() {
	var dbConn *gorm.DB
	var p *tasks.TaskProcessor
	var companiesXML = `<?xml version="1.0" encoding="UTF-8"?>
<result>
    <list>
        <corp_code>00434003</corp_code>
        <corp_name>다코</corp_name>
        <corp_eng_name>Daco corporation</corp_eng_name>
        <stock_code> </stock_code>
        <modify_date>20170630</modify_date>
    </list>
    <list>
        <corp_code>00430964</corp_code>
        <corp_name>굿앤엘에스</corp_name>
        <corp_eng_name>Good &amp; LS Co.,Ltd.</corp_eng_name>
        <stock_code> </stock_code>
        <modify_date>20170630</modify_date>
    </list>
</result>`

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
		zipDocument, err := testhelpers.CreateMockZipArchive("corpCode.xml", []byte(companiesXML))
		Expect(err).NotTo(HaveOccurred())

		testhelpers.New("https://opendart.fss.or.kr").Get("/api/corpCode.xml").Reply(200).Body(zipDocument).Header("Content-Type", "application/zip").Header("Content-Disposition", `attachment; filename="corpCode.zip"`)

		ctx := context.Background()
		err = p.HandleFetchCompaniesTask(ctx, asynq.NewTask(tasks.TypeTaskFetchCompanies, []byte("{}")))
		Expect(err).NotTo(HaveOccurred())

		companies, err := gorm.G[models.Company](dbConn).Order("corp_code DESC").Find(ctx)
		Expect(err).NotTo(HaveOccurred())
		Expect(companies).To(HaveLen(2))
		Expect(companies[0].CorpCode).To(Equal("00434003"))
		Expect(companies[0].CorpName).To(Equal("다코"))
		Expect(companies[0].CorpEngName).To(Equal("Daco corporation"))
		Expect(companies[0].LastModifiedDate).To(Equal(time.Date(2017, 6, 30, 0, 0, 0, 0, time.UTC)))
		Expect(companies[1].CorpCode).To(Equal("00430964"))
		Expect(companies[1].CorpName).To(Equal("굿앤엘에스"))
		Expect(companies[1].CorpEngName).To(Equal("Good & LS Co.,Ltd."))
		Expect(companies[1].LastModifiedDate).To(Equal(time.Date(2017, 6, 30, 0, 0, 0, 0, time.UTC)))
	})

	It("updates existing companies", func() {
		company := models.Company{
			CorpCode:         "00434003",
			CorpName:         "다코",
			CorpEngName:      "Old Daco corporation",
			LastModifiedDate: time.Date(2016, 6, 30, 0, 0, 0, 0, time.UTC),
		}

		ctx := context.Background()
		result := gorm.WithResult()
		err := gorm.G[models.Company](dbConn, result).Create(ctx, &company)
		Expect(err).NotTo(HaveOccurred())
		Expect(result.RowsAffected).To(Equal(int64(1)))

		zipDocument, err := testhelpers.CreateMockZipArchive("corpCode.xml", []byte(companiesXML))
		Expect(err).NotTo(HaveOccurred())

		testhelpers.New("https://opendart.fss.or.kr").Get("/api/corpCode.xml").Reply(200).Body(zipDocument).Header("Content-Type", "application/zip").Header("Content-Disposition", `attachment; filename="corpCode.zip"`)

		err = p.HandleFetchCompaniesTask(ctx, asynq.NewTask(tasks.TypeTaskFetchCompanies, []byte("{}")))
		Expect(err).NotTo(HaveOccurred())

		companies, err := gorm.G[models.Company](dbConn).Order("corp_code DESC").Find(ctx)
		Expect(err).NotTo(HaveOccurred())
		Expect(companies).To(HaveLen(2))
		Expect(companies[0].CorpCode).To(Equal("00434003"))
		Expect(companies[0].CorpName).To(Equal("다코"))
		Expect(companies[0].CorpEngName).To(Equal("Daco corporation"))
		Expect(companies[0].LastModifiedDate).To(Equal(time.Date(2017, 6, 30, 0, 0, 0, 0, time.UTC)))
		Expect(companies[1].CorpCode).To(Equal("00430964"))
		Expect(companies[1].CorpName).To(Equal("굿앤엘에스"))
		Expect(companies[1].CorpEngName).To(Equal("Good & LS Co.,Ltd."))
		Expect(companies[1].LastModifiedDate).To(Equal(time.Date(2017, 6, 30, 0, 0, 0, 0, time.UTC)))
	})
})
