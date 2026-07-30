package dart

import (
	"strings"

	"github.com/PuerkitoBio/goquery"
)

type DividendDecision struct {
	배당구분       string
	배당종류       string
	현물자산상세내역   string
	보통주_1주당배당금 string
	종류주_1주당배당금 string
	차등배당여부     string
	보통주_시가배당율  string
	종류주_시가배당율  string
	배당금총액      string
	배당기준일      string
	지급예정일자     string
	주주총회개최여부   string
	주주총회예정일자   string
	이사회결의일     string
	사외이사참석     string
	사외이사불참     string
	감사참석여부     string
	기타사항       string
	// and for the “종류주식에 대한 배당 관련 사항” subsection, maybe a slice of another struct
	StockTypeDetails []StockTypeDetail
}

type StockTypeDetail struct {
	종류주식명   string
	구분      string
	배당금_1주당 string
	시가배당율   string
	배당금총액   string
}

func ParseDividendHTML(htmlStr string) (*DividendDecision, error) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(htmlStr))
	if err != nil {
		return nil, err
	}

	var d DividendDecision

	// find the main table (first one)
	tblSel := doc.Find("table#XFormD1_Form0_Table0")
	if tblSel.Length() == 0 {
		// fallback, maybe first table
		tblSel = doc.Find("table").First()
	}

	// iterate rows
	tblSel.Find("tr").Each(func(i int, tr *goquery.Selection) {
		// in each row, cells come in pairs: <td> label, <td> value or more columns
		tds := tr.Find("td")
		if tds.Length() < 2 {
			return
		}
		// get label: usually first <td> or with a <span>
		label := strings.TrimSpace(tds.Eq(0).Text())
		// value: next cell (or next few depending on colspan)
		val := strings.TrimSpace(tds.Eq(1).Text())

		switch {
		case strings.Contains(label, "배당구분"):
			d.배당구분 = val
		case strings.Contains(label, "배당종류"):
			d.배당종류 = val
		case strings.Contains(label, "현물자산의 상세내역"):
			d.현물자산상세내역 = val
		case strings.Contains(label, "1주당 배당금"):
			// careful: this row has subrows. If it’s this label, you may skip and handle subrows
		case strings.Contains(label, "차등배당 여부"):
			d.차등배당여부 = val
		case strings.Contains(label, "배당금총액"):
			d.배당금총액 = val
		case strings.Contains(label, "배당기준일"):
			d.배당기준일 = val
		case strings.Contains(label, "배당금지급 예정일자"):
			d.지급예정일자 = val
		case strings.Contains(label, "주주총회 개최여부"):
			d.주주총회개최여부 = val
		case strings.Contains(label, "주주총회 예정일자"):
			d.주주총회예정일자 = val
		case strings.Contains(label, "이사회결의일"):
			d.이사회결의일 = val
		case strings.Contains(label, "사외이사 참석여부"):
			// here the row is “- 사외이사 참석여부 / 참석(명) / 불참(명)”
			// the label cell may span two rows; need to check sub-cells
			// one approach: treat this as two separate rows:
			// first row: tds[1] → 참석, next row: tds[1] → 불참
			d.사외이사참석 = val
		case strings.Contains(label, "감사 참석여부"):
			d.감사참석여부 = val
		case strings.Contains(label, "기타 투자판단과 관련한 중요사항"):
			d.기타사항 = val
		}
	})

	// parse the second table in “종류주식에 대한 배당 관련 사항”
	doc.Find("table#XFormG1_Form0_RepeatTable0").Each(func(_ int, stbl *goquery.Selection) {
		stbl.Find("tr").Each(func(i int, tr *goquery.Selection) {
			if i == 0 {
				// header row, skip
				return
			}
			tds := tr.Find("td")
			if tds.Length() >= 5 {
				detail := StockTypeDetail{
					종류주식명:   strings.TrimSpace(tds.Eq(0).Text()),
					구분:      strings.TrimSpace(tds.Eq(1).Text()),
					배당금_1주당: strings.TrimSpace(tds.Eq(2).Text()),
					시가배당율:   strings.TrimSpace(tds.Eq(3).Text()),
					배당금총액:   strings.TrimSpace(tds.Eq(4).Text()),
				}
				d.StockTypeDetails = append(d.StockTypeDetails, detail)
			}
		})
	})

	// Now, for the “1주당 배당금 / 시가배당율” subrows, we need to locate those two rows
	// The rows with rowspan=2 likely include the “보통주식 / 종류주식” labels.
	// So a second pass:
	tblSel.Find("tr").Each(func(i int, tr *goquery.Selection) {
		tds := tr.Find("td")
		if tds.Length() >= 3 {
			label := strings.TrimSpace(tds.Eq(0).Text())
			// If label contains “1주당 배당금” or “시가배당율”
			if strings.Contains(label, "1주당 배당금") {
				// next <td> is 보통주 text, third <td> is the value
				// tds[1] is "보통주식", tds[2] is the value
				d.보통주_1주당배당금 = strings.TrimSpace(tds.Eq(2).Text())
			}
			if strings.Contains(label, "시가배당율") {
				d.보통주_시가배당율 = strings.TrimSpace(tds.Eq(2).Text())
			}
		}
	})
	// Another pass for the “종류주식” subrows (second row of those two)
	tblSel.Find("tr").Each(func(i int, tr *goquery.Selection) {
		tds := tr.Find("td")
		if tds.Length() >= 3 {
			// If the first cell is empty (row continuation), but second cell is 종류주식
			second := strings.TrimSpace(tds.Eq(1).Text())
			if second == "종류주식" {
				d.종류주_1주당배당금 = strings.TrimSpace(tds.Eq(2).Text())
			}
			// also 시가배당율 second-row
			if strings.Contains(second, "종류주식") {
				// maybe next rows contain 시가배당율
				// you can also detect by context
			}
		}
	})

	return &d, nil
}
