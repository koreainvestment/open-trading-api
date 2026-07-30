package dart

import (
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type DisposalDoc struct {
	DocType  string        `json:"doc_type"` // "타법인 주식 및 출자증권 처분결정"
	RceptNo  string        `json:"rcept_no"` // (상위 로직에서 주입)
	CorpName string        `json:"corp_name"`
	Issuer   IssuerInfo    `json:"issuer"`
	Disposal DisposalInfo  `json:"disposal"`
	Post     PostOwnership `json:"post"`
	Purpose  string        `json:"purpose"`
	Schedule struct {
		DisposalDate       *time.Time `json:"disposal_date"`
		BoardDate          *time.Time `json:"board_date"`
		OutsideDirsPresent *int       `json:"outside_dirs_present"`
		OutsideDirsAbsent  *int       `json:"outside_dirs_absent"`
		AuditorPresent     *string    `json:"auditor_present"` // "-"면 nil 처리 가능
	}
	FTCReportRequired   *bool                       `json:"ftc_report_required"`
	PutOptionContracted *bool                       `json:"put_option_contracted"`
	PutOptionDetail     *string                     `json:"put_option_detail"`
	Notes               string                      `json:"notes"`      // 9. 기타
	Financials          map[string]FinancialSummary `json:"financials"` // "당해연도", "전년도", "전전년도"
}

func ParseDisposalHTML(raw string, rceptNo string) (*DisposalDoc, error) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(raw))
	if err != nil {
		return nil, err
	}

	out := &DisposalDoc{
		DocType:    "타법인 주식 및 출자증권 처분결정",
		RceptNo:    rceptNo,
		Financials: map[string]FinancialSummary{},
	}

	// 2) 메인 표
	mainTbl := doc.Find("#XFormD6_Form0_Table0")
	currentBlock := ""

	mainTbl.Find("tr").Each(func(_ int, tr *goquery.Selection) {
		tds := tr.Find("td")
		if tds.Length() == 0 {
			return
		}

		first := norm(tds.First().Text())
		// 블록 헤더?
		// 예: "1. 발행회사", "2. 처분내역", "3. 처분후소유주식수및지분비율"
		if strings.HasPrefix(first, "1발행회사") || strings.HasPrefix(first, "2처분내역") ||
			strings.HasPrefix(first, "3처분후소유주식수및지분비율") {
			currentBlock = first
			// 하위 라벨은 두 번째 셀부터
			if tds.Length() >= 3 {
				label := norm(tds.Eq(1).Text())
				value := cleanVal(tds.Last().Text())
				assign(out, currentBlock, label, value)
			}
			return
		}

		// 일반 라인: 첫 번째가 서브라벨
		if currentBlock != "" && tds.Length() >= 2 {
			label := norm(tds.Eq(0).Text())
			// 값은 보통 마지막 셀에 있습니다(일부 colspan)
			value := cleanVal(tds.Last().Text())
			assign(out, currentBlock, label, value)
		} else if strings.Contains(first, "기타투자판단과관련한중요사항") {
			// 9. 기타
			// 다음 tr의 마지막 td span이 본문
			// (이미 현재 tr에 colspan=5인 제목행이 있음)
		}
	})

	// 3) 기타 중요사항
	// "9. 기타..." 제목행 다음 tr의 마지막 td > span.xforms_input
	mainTbl.Find("tr").Each(func(i int, tr *goquery.Selection) {
		text := norm(tr.Text())
		if strings.Contains(text, "9기타투자판단과관련한중요사항") {
			next := tr.Next()
			if next.Length() > 0 {
				rawHTML, _ := next.Find("td span.xforms_input").Html()
				rawHTML = reComment.ReplaceAllString(rawHTML, "")
				rawHTML = reBrs.ReplaceAllString(rawHTML, "\n")
				out.Notes = strings.TrimSpace(strip(rawHTML))
			}
		}
	})

	// 4) 재무 요약 표
	finTbl := doc.Find("#XFormD6_Form0_Table2")
	finTbl.Find("tr").Each(func(i int, tr *goquery.Selection) {
		if i == 0 { // header
			return
		}
		tds := tr.Find("td")
		if tds.Length() < 9 {
			return
		}
		label := strings.TrimSpace(tds.Eq(0).Text()) // 당해 연도/전년도/전전년도
		fs := FinancialSummary{
			Assets:       toInt64Ptr(tds.Eq(1).Text()),
			Liabilities:  toInt64Ptr(tds.Eq(2).Text()),
			Equity:       toInt64Ptr(tds.Eq(3).Text()),
			Capital:      toInt64Ptr(tds.Eq(4).Text()),
			Revenue:      toInt64Ptr(tds.Eq(5).Text()),
			NetIncome:    toInt64Ptr(tds.Eq(6).Text()),
			AuditOpinion: strings.TrimSpace(tds.Eq(7).Text()),
			Auditor:      strings.TrimSpace(tds.Eq(8).Text()),
		}
		out.Financials[label] = fs
	})

	return out, nil
}

func isEucKR(s string) bool {
	// 매우 단순한 힌트: meta에 euc-kr가 있거나, 널 바이트가 섞인 한글 흔적
	ls := strings.ToLower(s)
	return strings.Contains(ls, "euc-kr") || strings.Contains(s, "charset=euc-kr")
}

func norm(s string) string {
	s = strings.TrimSpace(s)
	s = strings.ReplaceAll(s, " ", "")
	s = strings.ReplaceAll(s, ":", "")
	s = strings.ReplaceAll(s, "·", "")
	s = strings.ReplaceAll(s, "ㆍ", "")
	s = strings.ReplaceAll(s, "(", "")
	s = strings.ReplaceAll(s, ")", "")
	s = strings.ReplaceAll(s, "_", "")
	return s
}

func strip(s string) string {
	// 아주 간단한 태그 제거
	doc, _ := goquery.NewDocumentFromReader(strings.NewReader("<div>" + s + "</div>"))
	return strings.TrimSpace(doc.Find("div").Text())
}

func cleanVal(s string) string {
	return strings.TrimSpace(strings.ReplaceAll(s, "\u00a0", " "))
}

// 블록+라벨별로 out에 주입
func assign(out *DisposalDoc, block, label, value string) {
	switch {
	case strings.HasPrefix(block, "1발행회사"):
		switch label {
		case "회사명":
			out.CorpName, out.Issuer.Name = value, value
		case "국적":
			out.Issuer.Country = value
		case "대표자":
			out.Issuer.Representative = value
		case "자본금원":
			out.Issuer.Capital = toInt64Ptr(value)
		case "회사와관계":
			out.Issuer.Relation = value
		case "발행주식총수주":
			out.Issuer.SharesOutstanding = toInt64Ptr(value)
		case "주요사업":
			out.Issuer.Business = value
		}
	case strings.HasPrefix(block, "2처분내역"):
		switch label {
		case "처분주식수주":
			out.Disposal.Shares = toInt64Ptr(value)
		case "처분금액원":
			out.Disposal.AmountKRW = toInt64Ptr(value)
		case "자기자본원":
			out.Disposal.EquityKRW = toInt64Ptr(value)
		case "자기자본대비":
			out.Disposal.EquityRatio = toFloat64Ptr(value)
		case "대규모법인여부":
			out.Disposal.IsLargeCorp = boolFromKorean(value)
		}
	case strings.HasPrefix(block, "3처분후소유주식수및지분비율"):
		switch label {
		case "소유주식수주":
			out.Post.Shares = toInt64Ptr(value)
		case "지분비율":
			out.Post.Ratio = toFloat64Ptr(value)
		}
	default:
		// 4~8 일반 단일행 라벨
		switch label {
		case "처분목적":
			out.Purpose = value
		case "처분예정일자":
			out.Schedule.DisposalDate = toDatePtr(value)
		case "이사회결의일결정일":
			out.Schedule.BoardDate = toDatePtr(value)
		case "참석명":
			out.Schedule.OutsideDirsPresent = toIntOrNil(value)
		case "불참명":
			out.Schedule.OutsideDirsAbsent = toIntOrNil(value)
		case "감사사외이사가아닌감사위원참석여부":
			s := strings.TrimSpace(value)
			if s != "" && s != "-" {
				out.Schedule.AuditorPresent = &s
			}
		case "공정거래위원회신고대상여부":
			out.FTCReportRequired = boolFromKorean(value)
		case "풋옵션등계약의체결여부":
			out.PutOptionContracted = boolFromKorean(value)
		case "계약내용":
			if value != "-" && value != "" {
				out.PutOptionDetail = &value
			}
		}
	}
}
