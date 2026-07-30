package xbrl_test

import (
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"

	"kosis/internal/pkg/xbrl"
)

var _ = Describe("ParseHTML", func() {
	const sampleHTML = `
<DOCUMENT>
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
</DOCUMENT>
`

	var report xbrl.UsefulReport

	BeforeEach(func() {
		report = mustParseReport(sampleHTML)
	})

	It("captures metadata and key paragraphs", func() {
		Expect(report.ReportTitle).To(Equal("Form 10-K"))
		Expect(report.CompanyName).To(Equal("ACME Corp"))
		Expect(report.CompanyCIK).To(Equal("00001234"))
		Expect(report.KeyParagraphs).To(Equal([]string{
			"Primary discussion.",
			"Secondary paragraph",
		}))
	})

	It("collects table rows and cells in order", func() {
		Expect(report.Tables).To(HaveLen(2))
		Expect(report.Tables[0]).To(Equal([][]string{
			{"Metric", "Amount"},
			{"Revenue", "1000"},
			{"Profit", "500"},
		}))
		Expect(report.Tables[1]).To(Equal([][]string{
			{"Line Item", "Value"},
			{"Total Assets", "2000"},
		}))
	})
})

func mustParseReport(rawHTML string) xbrl.UsefulReport {
	GinkgoHelper()

	b, err := xbrl.ParseXBRL([]byte(rawHTML))
	Expect(err).NotTo(HaveOccurred())

	return *b
}
