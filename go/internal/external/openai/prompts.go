package openai

const (
	systemPrompt = `너의 임무는 한국 DART 공시 원문에서 사실과 수치를 추출해 정해진 JSON 스키마로만 출력하는 것이다. 추론은 최소화하고, 문서에 명시된 값만 사용하라.
  모든 공시 유형에 대해 다음 핵심 정보 카테고리는 반드시 세부 속성까지 식별하여 추출하라:
  1. 재무 및 수치 상세 (Financial Specifics): 총액(Total Amount)뿐만 아니라, 이를 구성하는 단가(Unit Price), 이자율(Rates), 비율(Ratios), 환율 등을 반드시 포함하라. 예: 주식수와 함께 '행사가격' 포함, 계약금액과 함께 '계약보증금률' 포함.
  2. 인물 및 대상의 속성 (Entity Attributes): 단순 이름/법인명 나열을 넘어, 해당 대상의 직위(Role), 관계(Relation), 상대방 정보(Counterparty)를 함께 명시하라. 예: '김형민' 대신 '대표이사 김형민', '소송' 시 '원고/피고' 구분.
  3. 시점과 기간 (Time & Period): '공시 제출일'과 구별되는 실제 발생일(Event Date), 계약 기간(Start/End), 만기일을 정확히 추출하라.
  4. 조건 및 제약 (Conditions & Terms): 단순 사실 외에 보호예수(Lock-up), 옵션(Put/Call), 해지 조건 등 수치에 영향을 주는 제약 사항을 포함하라.
	5. primary_cause: 이번 보고서가 제출된 핵심 사유를 한 문장으로 요약하라.
  6. details: 변동이 발생한 모든 주주(임원 포함)의 성명, 관계, 변동일, 구체적 사유, 변동 수량을 포함하여 하나의 자연스러운 문장으로 정리하라.
  공시 내 단순 중복은 제거하되, 위 핵심 카테고리에 해당하는 수치와 팩트는 생략 없이 모두 표시하라. 출력은 반드시 유효한 JSON 한 개만 반환하라. 설명문 금지.`

	// Securities Issuance Terms
	securitiesIssuanceTermsSchema = `
		스키마 필드: 
		doc_id, doc_type, issuer{name, areg_cik}, dates{first_filed, correction_announced}, 
		tranches[{name, seniority, amount_krw, coupon_before_pct, coupon_after_pct, coupon_delta_bp, annual_interest_delta_krw}], 
		totals{amount_krw, wac_before_pct, wac_after_pct, wac_delta_bp, annual_interest_delta_krw},
		reason_of_correction, spread_after_bp, 
		impact_score{equity_impact_0to5, credit_impact_0to5, liquidity_impact_0to5}, notes.
		단위와 포맷:
		- 금액은 정수 KRW.
		- 퍼센트는 소수점 4자리 이내.
		- bp 계산: (정정후 - 정정전)*10000. 
		- 연간 이자 증분은 amount_krw*(coupon_after - coupon_before).
	`
	additionalSecuritiesIssuanceTermsSchema = `
- "증권발행조건확정" 표에서 각 트랜치의 정정전/정정후 금리를 읽어라.
- "모집 또는 매출금액" 문단에서 각 트랜치 금액을 읽어라.
- seniority는 '선순위/후순위'로 추론 가능할 때만 표기하고, 없으면 null.
- impact_score는 다음 기준의 휴리스틱을 적용:
  - equity_impact: SPC 금리 확정 정정은 0~1.
  - credit_impact: 금리 변화가 25bp 미만이면 1, 25~75bp면 2, 그 이상 3.
  - liquidity_impact: 모집액이 1천억 미만이면 0.5, 1천억 이상이면 1.0.`

	supplySchema = `스키마 필드: {
	doc_id, corp_name, report_title, event_code, amendment{reason, prev_amount_krw, new_amount_krw, prev_ratio_to_sales, new_ratio_to_sales}, contract{name, counterparty, amount_krw, company_recent_sales_krw, counterparty_recent_sales_krw, country, term_from, term_to, progress_pct}, score{direction: string, magnitude: float64, confidence: float64, horizons: []string, rationale_short: string}}.
	단위와 포맷:
	- 금액은 정수 KRW.
	- 퍼센트는 소수점 4자리 이내.`

	reportSchema = `스키마 필드: {
		company_name: string,
		period_start_date: string (YYYY-MM-DD),
		period_end_date: string (YYYY-MM-DD),
		submission_date: string (YYYY-MM-DD),
		share_info: {
			issued_common_shares: int64,
			par_value_krw: int64,
			capital_million_krw: int64,
			outstanding_common_shares: int64
		},
		sales_breakdown_million_krw: {
			segment: string,
			export: int64,
			domestic: int64,
			total: int64
		},
		consolidated_financials_million_krw: {
			balance_sheet: {
				"period_YYYY_MM_DD": {
					total_assets: int64,
					total_liabilities: int64,
					total_equity: int64,
					equity_attributable_to_owners: int64,
					non_controlling_interests: int64,
					capital: int64
				}
			},
			income_statement: {
				"period_YYYY_H1" 또는 "period_YYYY": {
					sales: int64,
					operating_income: int64,
					net_income: int64,
					owners_net_income: int64
				}
			}
		},
		separate_financials_million_krw: {
			balance_sheet: {
				"period_YYYY_MM_DD": {
					total_assets: int64,
					total_liabilities: int64,
					total_equity: int64,
					capital: int64
				}
			},
			income_statement: {
				"period_YYYY_H1" 또는 "period_YYYY": {
					sales: int64,
					operating_income: int64,
					net_income: int64
				}
			}
		},
		fx_exposure_million_krw: {
			current_period_end: {
				assets: {
					USD: int64,
					EUR: int64,
					JPY: int64,
					CNY_etc: int64
				},
				liabilities: {
					USD: int64,
					EUR: int64,
					JPY: int64,
					CNY_etc: int64
				}
			}
		},
		fx_sensitivity_10pct_million_krw: {
			current_period_end: {
				USD: {
					profit_loss_if_up: int64,
					profit_loss_if_down: int64
				},
				EUR: {
					profit_loss_if_up: int64,
					profit_loss_if_down: int64
				},
				JPY: {
					profit_loss_if_up: int64,
					profit_loss_if_down: int64
				},
				CNY_etc: {
					profit_loss_if_up: int64,
					profit_loss_if_down: int64
				}
			}
		},
		derivatives_valuation_effects_million_krw: {
			forward_fx_loss: int64,
			cross_currency_swap_loss: int64,
			total_loss: int64
		},
		production_capacity: {
			current_half_year: {
				capacity_million_krw: int64,
				production_million_krw: int64,
				utilization_percent: float64
			},
			prior_year: {
				utilization_percent: float64
			}
		},
		rnd: {
			expenses_million_krw: {
				period_2025_H1_total: int64
			}
		},
		market_share: {
			product: string,
			period_2025_H1_percent: float64,
			period_2024_percent: float64,
			period_2023_percent: float64
		},
		capex: {
			amount_hundred_million_krw: int64,
			period: string
		},
		cash_flows_consolidated_million_krw: {
			period_2025_H1: {
				operating: int64,
				investing: int64,
				financing: int64,
				ending_cash: int64,
				beginning_cash: int64
			}
		},
		credit_ratings: [
			{
				date: string,
				agency: string,
				subject: string,
				rating: string
			}
		]
	}.
	단위와 포맷:
	- 모든 금액은 정수로 표시하며, 단위는 백만원(KRW)입니다. 단, capex의 amount_hundred_million_krw는 억원 단위입니다.
	- 날짜는 YYYY-MM-DD 형식으로 표시합니다.
	- 퍼센트는 소수점 2자리 이내의 float64로 표시합니다 (예: 85.5).
	- 문서에 명시되지 않은 필드는 null이 아닌 0 또는 빈 문자열로 표시합니다.
	- credit_ratings는 배열이며, 정보가 없으면 빈 배열 []로 표시합니다.
	- consolidated_financials_million_krw와 separate_financials_million_krw의 balance_sheet와 income_statement는 객체(map) 형태이며, 키는 기간을 나타내는 문자열입니다.
	- balance_sheet의 키 형식: "period_YYYY_MM_DD" (예: "period_2025_06_30", "period_2024_12_31")
	- income_statement의 키 형식: "period_YYYY_H1" (반기) 또는 "period_YYYY" (연간) (예: "period_2025_H1", "period_2024")
	- 각 기간별로 문서에 있는 모든 재무제표 데이터를 해당 키로 추출합니다.
	- 연결재무제표와 별도재무제표를 구분하여 정확히 추출합니다.
	- 외화노출액과 외화민감도는 각 통화별로 구분하여 추출합니다.`

	additionalReportSchema = `
	- 회사명, 보고기간, 제출일자는 문서 상단에서 확인합니다.
	- 주식정보는 발행주식수, 액면가, 자본금, 유통주식수를 정확히 추출합니다.
	- 매출구성은 사업부문별, 수출/내수 구분하여 추출합니다.
	- 재무제표는 연결/별도 구분하여 각 기간별로 추출합니다.
	- 외화노출은 자산/부채별, 통화별로 구분하여 추출합니다.
	- 외화민감도는 각 통화별로 10% 상승/하락 시 손익을 추출합니다.
	- 파생상품평가는 선물환 손실, 통화스왑 손실, 합계를 추출합니다.
	- 생산능력은 당기 반기와 전년도 가동률을 추출합니다.
	- R&D 비용은 당기 반기 합계를 추출합니다.
	- 시장점유율은 제품명과 각 기간별 점유율을 추출합니다.
	- 자본지출은 금액(억원)과 해당 기간을 추출합니다.
	- 현금흐름은 영업/투자/재무 활동별로 추출합니다.
	- 신용등급은 날짜, 평가기관, 평가대상, 등급을 추출합니다.
	- 모든 숫자는 문서에 명시된 값만 사용하며, 계산이나 추론은 하지 않습니다.`

	defaultSchema = `
	스키마 필드: {
		company_name: string,
		date: string (YYYY-MM-DD),
		type: string (예: '사업보고서', '분기보고서' 등, 명확히 명시되어 있지 않으면 빈 문자열 사용),
		summary: string,
		related_companies: [string] (연관된 회사 이름 배열, 없을 경우 빈 배열 []),
		schema_suggestion: string (추출된 데이터에 적합한 JSON 스키마 예시, 아래 Output Format 참고)
		primary_cause: string,
		details: string,
		data_extraction: {
    financial_specifics: [
      {
        item: string,
        value: string,
        unit: string,
        details: string
      }
    ],
    entity_attributes: [
      {
        name: string,
        role: string,
        relationship: string,
        identifier: string
      }
    ],
    time_period: [
      {
        label: string,
        date: string,
        note: string
      }
    ],
    conditions_terms: [
      {
        term_name: string,
        content: string
      }
    ]
	}
	## Output Format
		- 항상 아래의 필드명 및 순서(company_name, date, type, summary, related_companies, schema_suggestion)에 맞추어 유효한 JSON 오브젝트 하나만 출력.
		- 문서에 값이 부재/불분명하면 해당 필드는 빈 문자열("") 또는 빈 배열([])로 출력.
		- schema_suggestion 필드는 위에 제시된 스키마를 그대로 문자열로 입력.
		- 불완전/오류 입력 데이터도 동일한 규칙을 적용해 출력.
	예시:
	{
		"company_name": "삼성전자",
		"date": "2023-09-30",
		"type": "사업보고서",
		"summary": "2023년 3분기에 매출이 10% 증가하였음.",
		"related_companies": ["삼성디스플레이"],
		"schema_suggestion": "{company_name: string, date: string (YYYY-MM-DD), type: string, summary: string, related_companies: [string], schema_suggestion: string}"
	}
	## Output Verbosity
	- 반드시 출력은 1개의 JSON 오브젝트만 반환할 것.
	- 어떤 중간 설명, 변명, 인사말도 추가하지 말 것.
	- 정해진 필드만 사용하고 예시보다 길거나 추가 정보 없이 1줄씩 간결하게 작성할 것. (2문장 이하 요약)
	- 완결성 우선: 값이 부족해도 누락 없이 모든 필드 채우기. 답변은 늘 위 JSON 스키마에 맞춰 완전하게 채우는 것이 언어의 간결함보다 우선됨.`

	defaultAdditionalSchema = `
	- 회사명, 날짜, 유형, 요약은 문서 상단에서 확인합니다.
	- 요약은 문서 내용을 요약한 문자열로 추출합니다.
	- 유형은 문서 유형을 추출합니다.
	- 날짜는 문서 날짜를 추출합니다.
	- 회사명은 문서 회사명을 추출합니다.
	- 관련 회사는 문서 내용에서 관련 회사를 추출합니다.
	- 해당 문서에 맞는 JSON 스키마를 제안합니다.`
)
