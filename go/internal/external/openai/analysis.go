package openai

type TrendMetrics struct {
	Period          string
	Sales           int64
	OwnersNetIncome int64
	OperatingMargin float64
	DebtRatio       float64
	MarketShare     float64
	UtilizationRate float64
}

func analyzeTrends(report *Report) map[string]TrendMetrics {
	metrics := make(map[string]TrendMetrics)

	// 데이터 추출 및 계산 헬퍼 함수
	extract := func(period, isKey, bsKey string, ms float64, util float64) TrendMetrics {
		m := TrendMetrics{Period: period, MarketShare: ms, UtilizationRate: util}

		// 손익계산서 데이터 추출 및 영업이익률 계산
		if is, ok := report.Consolidated.IncomeStatement[isKey]; ok {
			m.Sales = is.Sales
			m.OwnersNetIncome = is.OwnersNetIncome
			if is.Sales != 0 {
				m.OperatingMargin = (float64(is.OperatingIncome) / float64(is.Sales)) * 100
			}
		}

		// 재무상태표 데이터 추출 및 부채비율 계산
		if bs, ok := report.Consolidated.BalanceSheet[bsKey]; ok {
			if bs.TotalEquity != 0 {
				// 부채비율 = (부채총계 / 자본총계) * 100
				m.DebtRatio = (float64(bs.TotalLiabilities) / float64(bs.TotalEquity)) * 100
			}
		}
		return m
	}

	// 기간별 데이터 추출
	metrics["2023"] = extract("2023", "period_2023", "period_2023_12_31",
		report.MarketShare.FY2023, report.Production.PriorYear.UtilizationPct)
	metrics["2024"] = extract("2024", "period_2024", "period_2024_12_31",
		report.MarketShare.FY2024, report.Production.PriorYear.UtilizationPct)
	metrics["2025H1"] = extract("2025 H1", "period_2025_H1", "period_2025_06_30",
		report.MarketShare.H12025, report.Production.CurrentHalfYear.UtilizationPct)

	return metrics
}
