package dart

import (
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type AcquisitionDoc struct {
	DocType  string        `json:"doc_type"`
	RceptNo  string        `json:"rcept_no"`
	CorpName string        `json:"corp_name"`
	Issuer   IssuerInfo    `json:"issuer"`
	Acquire  AcquireInfo   `json:"acquire"`
	Post     PostOwnership `json:"post"`
	Method   string        `json:"method"`
	Purpose  string        `json:"purpose"`
	Schedule struct {
		PlannedDate        *time.Time `json:"planned_date"`
		BoardDate          *time.Time `json:"board_date"`
		OutsideDirsPresent *int       `json:"outside_dirs_present"`
		OutsideDirsAbsent  *int
		AuditorPresent     *string `json:"auditor_present"`
	}
	MajorReportRequired *bool                       `json:"major_report_required"`
	ReverseListing      *bool                       `json:"reverse_listing"`
	Plan3rdPartyAlloc   *string                     `json:"plan_3rd_party_alloc"`
	TargetMeetsReverse  *string                     `json:"target_meets_reverse"`
	FTCReportRequired   *bool                       `json:"ftc_report_required"`
	PutOptionContracted *bool                       `json:"put_option_contracted"`
	PutOptionDetail     *string                     `json:"put_option_detail"`
	Notes               string                      `json:"notes"`
	Financials          map[string]FinancialSummary `json:"financials"`
}

type AcquireInfo struct {
	Shares            *int64   `json:"shares"`
	AmountKRW         *int64   `json:"amount_krw"`
	EquityKRW         *int64   `json:"equity_krw"`
	EquityRatio       *float64 `json:"equity_ratio"`         // %
	AssetTotal        *int64   `json:"asset_total"`          // 최근 사업연도말 자산총액
	PriceToAssetRatio *float64 `json:"price_to_asset_ratio"` // 취득가액/자산총액(%)
	IsLargeCorp       *bool    `json:"is_large_corp"`
}

// ParseAcquisitionHTML merges amendment wrapper (정정신고) with the base "타법인 주식 및 출자증권 취득결정"
func ParseAcquisitionHTML(raw string, rceptNo string) (*AcquisitionDoc, error) {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(raw))
	if err != nil {
		return nil, err
	}

	out := &AcquisitionDoc{
		DocType:    "타법인 주식 및 출자증권 취득결정",
		RceptNo:    rceptNo,
		Financials: map[string]FinancialSummary{},
	}

	// --- Amendment (정정) 수집: 정정전/정정후 테이블에서 "정정후"만 집계
	amend := map[string]string{}
	doc.Find("#XFormD8_Form0_RepeatTable0 tr").Each(func(_ int, tr *goquery.Selection) {
		tds := tr.Find("td")
		if tds.Length() != 3 {
			return
		}
		label := strings.ReplaceAll(textOf(tds.Eq(0)), "\n", "")
		next := strings.TrimSpace(textOf(tds.Eq(2)))
		switch {
		case strings.Contains(label, "취득금액(원)"):
			amend["취득금액(원)"] = next
		case strings.Contains(label, "자기자본대비"):
			amend["자기자본대비(%)"] = next
		case strings.Contains(label, "취득가액/자산총액"):
			amend["취득가액/자산총액(%)"] = next
		case strings.Contains(label, "취득예정일자"):
			amend["취득예정일자"] = next
		case strings.Contains(label, "기타 투자판단과 관련한 중요사항"):
			amend["기타"] = strings.ReplaceAll(next, "\n", " ")
		}
	})

	// --- 본문 메인 테이블
	base := doc.Find("#XFormD6_Form0_Table0")
	current := ""
	base.Find("tr").Each(func(_ int, tr *goquery.Selection) {
		tds := tr.Find("td")
		if tds.Length() == 0 {
			return
		}
		first := textOf(tds.First())

		if strings.Contains(first, "1. 발행회사") {
			current = "issuer"
			return
		}
		if strings.Contains(first, "2. 취득내역") {
			current = "acquire"
			return
		}
		if strings.Contains(first, "3. 취득후 소유주식수 및 지분비율") {
			current = "post"
			return
		}

		if current == "issuer" && tds.Length() >= 2 {
			label := strings.TrimSpace(textOf(tds.Eq(0)))
			val := strings.TrimSpace(textOf(tds.Last()))
			switch label {
			case "회사명":
				out.CorpName = val
				out.Issuer.Name = val
			case "국적":
				out.Issuer.Country = val
			case "대표자":
				out.Issuer.Representative = strings.ReplaceAll(val, "\n", ", ")
			case "자본금(원)":
				out.Issuer.Capital = toInt64Ptr(val)
			case "회사와 관계":
				out.Issuer.Relation = val
			case "발행주식총수(주)":
				out.Issuer.SharesOutstanding = toInt64Ptr(val)
			case "주요사업":
				out.Issuer.Business = val
			}
			return
		}

		if current == "acquire" && tds.Length() >= 2 {
			label := strings.TrimSpace(textOf(tds.Eq(0)))
			val := strings.TrimSpace(textOf(tds.Last()))
			switch label {
			case "취득주식수(주)":
				out.Acquire.Shares = toInt64Ptr(val)
			case "취득금액(원)":
				if v, ok := amend["취득금액(원)"]; ok {
					val = v
				}
				out.Acquire.AmountKRW = toInt64Ptr(val)
			case "자기자본(원)":
				out.Acquire.EquityKRW = toInt64Ptr(val)
			case "자기자본대비(%)":
				if v, ok := amend["자기자본대비(%)"]; ok {
					val = v
				}
				out.Acquire.EquityRatio = toFloat64Ptr(val)
			case "대규모법인여부":
				out.Acquire.IsLargeCorp = boolFromKorean(val)
			}
			return
		}

		if current == "post" && tds.Length() >= 2 {
			label := strings.TrimSpace(textOf(tds.Eq(0)))
			val := strings.TrimSpace(textOf(tds.Last()))
			switch label {
			case "소유주식수(주)":
				out.Post.Shares = toInt64Ptr(val)
			case "지분비율(%)":
				out.Post.Ratio = toFloat64Ptr(val)
			}
			return
		}

		// 단일행(4~13)
		if tds.Length() >= 3 {
			label := strings.TrimSpace(textOf(tds.Eq(0)))
			val := strings.TrimSpace(textOf(tds.Eq(2)))
			switch {
			case strings.HasPrefix(label, "4. 취득방법"):
				out.Method = val
			case strings.HasPrefix(label, "5. 취득목적"):
				out.Purpose = val
			case strings.HasPrefix(label, "6. 취득예정일자"):
				if v, ok := amend["취득예정일자"]; ok {
					val = v
				}
				out.Schedule.PlannedDate = toDatePtr(val)
			case strings.HasPrefix(label, "7. 자산양수의 주요사항보고서 제출대상 여부"):
				out.MajorReportRequired = boolFromKorean(val)
			case strings.Contains(label, "최근 사업연도말 자산총액"):
				out.Acquire.AssetTotal = toInt64Ptr(textOf(tds.Eq(2)))
				out.Acquire.PriceToAssetRatio = toFloat64Ptr(textOf(tds.Eq(4)))
				if v, ok := amend["취득가액/자산총액(%)"]; ok {
					out.Acquire.PriceToAssetRatio = toFloat64Ptr(v)
				}
			case strings.HasPrefix(label, "8. 우회상장 해당 여부"):
				out.ReverseListing = boolFromKorean(val)
			case strings.Contains(label, "제3자배정"):
				out.Plan3rdPartyAlloc = &val
			case strings.HasPrefix(label, "9. 발행회사(타법인)의 우회상장 요건 충족여부"):
				out.TargetMeetsReverse = &val
			case strings.HasPrefix(label, "10. 이사회결의일"):
				out.Schedule.BoardDate = toDatePtr(val)
			case strings.Contains(label, "사외이사 참석여부") && strings.Contains(textOf(tds.Eq(1)), "참석(명)"):
				out.Schedule.OutsideDirsPresent = intPtrFrom(textOf(tds.Eq(2)))
			case strings.Contains(label, "사외이사 참석여부") && strings.Contains(textOf(tds.Eq(1)), "불참(명)"):
				out.Schedule.OutsideDirsAbsent = intPtrFrom(textOf(tds.Eq(2)))
			case strings.Contains(label, "감사(사외이사가 아닌 감사위원)참석여부"):
				s := strings.TrimSpace(val)
				if s != "" && s != "-" {
					out.Schedule.AuditorPresent = &s
				}
			case strings.HasPrefix(label, "11. 공정거래위원회 신고대상 여부"):
				out.FTCReportRequired = boolFromKorean(val)
			case strings.HasPrefix(label, "12. 풋옵션 등 계약 체결여부"):
				out.PutOptionContracted = boolFromKorean(val)
			case strings.HasPrefix(label, "-계약내용"):
				if val != "" && val != "-" {
					out.PutOptionDetail = &val
				}
			case strings.HasPrefix(label, "13. 기타"):
				notes := strings.TrimSpace(base.Find("tr").Eq(base.Find("tr").Index() + 1).Find("td").Last().Text())
				if notes == "" {
					notes = val
				}
				if v, ok := amend["기타"]; ok && v != "" {
					if notes != "" {
						notes = notes + "\n\n[정정후] " + v
					} else {
						notes = v
					}
				}
				out.Notes = notes
			}
		}
	})

	// --- 재무요약
	doc.Find("#XFormD6_Form0_Table2 tr").Each(func(i int, tr *goquery.Selection) {
		if i == 0 {
			return
		} // header
		tds := tr.Find("td")
		if tds.Length() < 9 {
			return
		}
		label := strings.TrimSpace(textOf(tds.Eq(0)))
		fs := FinancialSummary{
			Assets:       toInt64Ptr(textOf(tds.Eq(1))),
			Liabilities:  toInt64Ptr(textOf(tds.Eq(2))),
			Equity:       toInt64Ptr(textOf(tds.Eq(3))),
			Capital:      toInt64Ptr(textOf(tds.Eq(4))),
			Revenue:      toInt64Ptr(textOf(tds.Eq(5))),
			NetIncome:    toInt64Ptr(textOf(tds.Eq(6))),
			AuditOpinion: strings.TrimSpace(textOf(tds.Eq(7))),
			Auditor:      strings.TrimSpace(textOf(tds.Eq(8))),
		}
		out.Financials[label] = fs
	})

	return out, nil
}
