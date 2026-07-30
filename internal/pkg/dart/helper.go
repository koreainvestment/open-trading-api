package dart

import (
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type IssuerInfo struct {
	Name              string `json:"name"`
	Country           string `json:"country"`
	Representative    string `json:"representative"`
	Capital           *int64 `json:"capital"`
	Relation          string `json:"relation"` // 자회사 등
	SharesOutstanding *int64 `json:"shares_outstanding"`
	Business          string `json:"business"`
}

type DisposalInfo struct {
	Shares      *int64   `json:"shares"`
	AmountKRW   *int64   `json:"amount_krw"`
	EquityKRW   *int64   `json:"equity_krw"`
	EquityRatio *float64 `json:"equity_ratio"`  // %
	IsLargeCorp *bool    `json:"is_large_corp"` // 해당/미해당
}

type PostOwnership struct {
	Shares *int64   `json:"shares"`
	Ratio  *float64 `json:"ratio"` // %
}

type FinancialSummary struct {
	Assets       *int64 `json:"assets"`
	Liabilities  *int64 `json:"liabilities"`
	Equity       *int64 `json:"equity"`
	Capital      *int64 `json:"capital"`
	Revenue      *int64 `json:"revenue"`
	NetIncome    *int64 `json:"net_income"`
	AuditOpinion string `json:"audit_opinion"`
	Auditor      string `json:"auditor"`
}

var (
	reDigits  = regexp.MustCompile(`[,\s]`)
	reBrs     = regexp.MustCompile(`(?i)<br\s*/?>`)
	reComment = regexp.MustCompile(`<!--\?[^>]*\?-->`)
)

func toInt64Ptr(s string) *int64 {
	s = strings.TrimSpace(s)
	if s == "" || s == "-" {
		return nil
	}
	s = reDigits.ReplaceAllString(s, "")
	if s == "" {
		return nil
	}
	v, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		return nil
	}
	return &v
}

func toFloat64Ptr(s string) *float64 {
	s = strings.TrimSpace(s)
	if s == "" || s == "-" {
		return nil
	}
	s = strings.ReplaceAll(s, "%", "")
	s = strings.ReplaceAll(s, ",", "")
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return nil
	}
	return &f
}

func toDatePtr(s string) *time.Time {
	s = strings.TrimSpace(s)
	if s == "" || s == "-" {
		return nil
	}

	// 주로 YYYY-MM-DD
	if t, err := time.Parse("2006-01-02", s); err == nil {
		return &t
	}
	return nil
}

func boolFromKorean(s string) *bool {
	s = strings.TrimSpace(s)
	if s == "" || s == "-" {
		return nil
	}
	switch s {
	case "해당", "예", "있음", "Yes", "yes":
		v := true
		return &v
	case "미해당", "아니오", "없음", "No", "no":
		v := false
		return &v
	}
	return nil
}

func textOf(sel *goquery.Selection) string {
	return strings.TrimSpace(sel.Text())
}

func intPtrFrom(s string) *int {
	s = reDigits.ReplaceAllString(strings.TrimSpace(s), "")
	if s == "" {
		return nil
	}
	v, err := strconv.Atoi(s)
	if err != nil {
		return nil
	}
	return &v
}

func toIntOrNil(s string) *int {
	s = strings.TrimSpace(s)
	if s == "" || s == "-" {
		return nil
	}
	s = reDigits.ReplaceAllString(s, "")
	v, err := strconv.Atoi(s)
	if err != nil {
		return nil
	}
	return &v
}
