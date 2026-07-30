package openai

import "encoding/json"

type Report struct {
	CompanyName    string `json:"company_name"`
	PeriodStart    string `json:"period_start_date"` // YYYY-MM-DD
	PeriodEnd      string `json:"period_end_date"`
	SubmissionDate string `json:"submission_date"`

	ShareInfo      ShareInfo      `json:"share_info"`
	SalesBreakdown SalesBreakdown `json:"sales_breakdown_million_krw"`

	Consolidated Consolidated `json:"consolidated_financials_million_krw"`
	Separate     Separate     `json:"separate_financials_million_krw"`

	FXExp  FXExposure    `json:"fx_exposure_million_krw"`
	FXSens FXSensitivity `json:"fx_sensitivity_10pct_million_krw"`

	DerivPnl DerivValuation `json:"derivatives_valuation_effects_million_krw"`

	Production  ProductionCap `json:"production_capacity"`
	RnD         RnD           `json:"rnd"`
	MarketShare MarketShare   `json:"market_share"`
	Capex       Capex         `json:"capex"`

	CashFlows CashFlows `json:"cash_flows_consolidated_million_krw"`

	CreditRatings []CreditRating `json:"credit_ratings"`

	Raw json.RawMessage `json:"-"`
}

type ShareInfo struct {
	IssuedCommon      int64 `json:"issued_common_shares"`
	ParValueKRW       int64 `json:"par_value_krw"`
	CapitalMilKRW     int64 `json:"capital_million_krw"`
	OutstandingCommon int64 `json:"outstanding_common_shares"`
}

type SalesBreakdown struct {
	Segment  string `json:"segment"`
	Export   int64  `json:"export"`
	Domestic int64  `json:"domestic"`
	Total    int64  `json:"total"`
}

type Consolidated struct {
	BalanceSheet    map[string]BS `json:"balance_sheet"`
	IncomeStatement map[string]IS `json:"income_statement"`
}

type Separate struct {
	BalanceSheet    map[string]BS2 `json:"balance_sheet"`
	IncomeStatement map[string]IS2 `json:"income_statement"`
}

type BS struct {
	TotalAssets             int64 `json:"total_assets"`
	TotalLiabilities        int64 `json:"total_liabilities"`
	TotalEquity             int64 `json:"total_equity"`
	EquityOwners            int64 `json:"equity_attributable_to_owners"`
	NonControllingInterests int64 `json:"non_controlling_interests"`
	Capital                 int64 `json:"capital"`
}

type IS struct {
	Sales           int64 `json:"sales"`
	OperatingIncome int64 `json:"operating_income"`
	NetIncome       int64 `json:"net_income"`
	OwnersNetIncome int64 `json:"owners_net_income"`
}

type BS2 struct {
	TotalAssets      int64 `json:"total_assets"`
	TotalLiabilities int64 `json:"total_liabilities"`
	TotalEquity      int64 `json:"total_equity"`
	Capital          int64 `json:"capital"`
}

type IS2 struct {
	Sales           int64 `json:"sales"`
	OperatingIncome int64 `json:"operating_income"`
	NetIncome       int64 `json:"net_income"`
}

type FXExposure struct {
	CurrentPeriodEnd struct {
		Assets      CurrencyVec `json:"assets"`
		Liabilities CurrencyVec `json:"liabilities"`
	} `json:"current_period_end"`
}
type CurrencyVec struct {
	USD    int64 `json:"USD"`
	EUR    int64 `json:"EUR"`
	JPY    int64 `json:"JPY"`
	CNYEtc int64 `json:"CNY_etc"`
}

type FXSensitivity struct {
	CurrentPeriodEnd struct {
		USD    UpDown `json:"USD"`
		EUR    UpDown `json:"EUR"`
		JPY    UpDown `json:"JPY"`
		CNYEtc UpDown `json:"CNY_etc"`
	} `json:"current_period_end"`
}
type UpDown struct {
	ProfitLossIfUp   int64 `json:"profit_loss_if_up"`
	ProfitLossIfDown int64 `json:"profit_loss_if_down"`
}

type DerivValuation struct {
	ForwardFXLoss         int64 `json:"forward_fx_loss"`
	CrossCurrencySwapLoss int64 `json:"cross_currency_swap_loss"`
	TotalLoss             int64 `json:"total_loss"`
}

type ProductionCap struct {
	CurrentHalfYear struct {
		CapacityMilKRW   int64   `json:"capacity_million_krw"`
		ProductionMilKRW int64   `json:"production_million_krw"`
		UtilizationPct   float64 `json:"utilization_percent"`
	} `json:"current_half_year"`
	PriorYear struct {
		UtilizationPct float64 `json:"utilization_percent"`
	} `json:"prior_year"`
}

type RnD struct {
	Expenses struct {
		H12025Total int64 `json:"period_2025_H1_total"`
	} `json:"expenses_million_krw"`
}

type MarketShare struct {
	Product string  `json:"product"`
	H12025  float64 `json:"period_2025_H1_percent"`
	FY2024  float64 `json:"period_2024_percent"`
	FY2023  float64 `json:"period_2023_percent"`
}

type Capex struct {
	AmountHundredMillionKRW int64  `json:"amount_hundred_million_krw"`
	Period                  string `json:"period"`
}

type CashFlows struct {
	H12025 struct {
		Operating     int64 `json:"operating"`
		Investing     int64 `json:"investing"`
		Financing     int64 `json:"financing"`
		EndingCash    int64 `json:"ending_cash"`
		BeginningCash int64 `json:"beginning_cash"`
	} `json:"period_2025_H1"`
}

type CreditRating struct {
	Date    string `json:"date"`
	Agency  string `json:"agency"`
	Subject string `json:"subject"`
	Rating  string `json:"rating"`
}

type DefaultReport struct {
	CompanyName      string         `json:"company_name"`
	Date             string         `json:"date"`
	Type             string         `json:"type"`
	Summary          string         `json:"summary"`
	PrimaryCause     string         `json:"primary_cause"`
	Details          string         `json:"details"`
	RelatedCompanies []string       `json:"related_companies"`
	SchemaSuggestion string         `json:"schema_suggestion"`
	DataExtraction   DataExtraction `json:"data_extraction"`
}

type DataExtraction struct {
	FinancialSpecifics []FinancialSpecific `json:"financial_specifics"`
	EntityAttributes   []EntityAttribute   `json:"entity_attributes"`
	TimePeriod         []TimePeriod        `json:"time_period"`
	ConditionsTerms    []ConditionsTerm    `json:"conditions_terms"`
}

type FinancialSpecific struct {
	Item    string `json:"item"`
	Value   string `json:"value"`
	Unit    string `json:"unit"`
	Details string `json:"details"`
}

type EntityAttribute struct {
	Name         string `json:"name"`
	Role         string `json:"role"`
	Relationship string `json:"relationship"`
	Identifier   string `json:"identifier"`
}

type TimePeriod struct {
	Label string `json:"label"`
	Date  string `json:"date"`
	Note  string `json:"note"`
}

type ConditionsTerm struct {
	TermName string `json:"term_name"`
	Content  string `json:"content"`
}
