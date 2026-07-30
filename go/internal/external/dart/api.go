package dart

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"time"
)

type ReportType string

const FIRST_QUARTER = ReportType("11013")   // 1분기
const HALF_YEAR = ReportType("11012")       // 반기
const THIRD_QUARTER = ReportType("11014")   // 3분기
const BUSINESS_REPORT = ReportType("11011") // 사업보고서

type PeriodicReport struct {
	Status  string            `json:"status"`
	Message string            `json:"message"`
	List    []GetAlotmentItem `json:"list"`
}

type GetAlotmentItem struct {
	RceptNo  string `json:"rcept_no"`
	CorpCode string `json:"corp_code"`
	CorpName string `json:"corp_name"`
	Se       string `json:"se"`
	StockKnd string `json:"stock_knd"`
	Thstrm   string `json:"thstrm"`
	Frmtrm   string `json:"frmtrm"`
	Lwfr     string `json:"lwfr"`
	StlmDt   string `json:"stlm_dt"`
}

// 배당에 관한 사항 개발가이드
// https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002&apiId=2019005
func (c *DartClient) getAlotment(corpCode, bisnsYear string, reportCode ReportType) ([]GetAlotmentItem, error) {
	u, _ := url.Parse(baseURL + "/alotMatter.json")
	q := u.Query()
	q.Set("crtfc_key", c.key)               // API Key
	q.Set("corp_code", corpCode)            // 8자리 기업코드(예: 삼성전자 00126380)
	q.Set("bsns_year", bisnsYear)           // 사업연도
	q.Set("reprt_code", string(reportCode)) // 보고서 코드

	u.RawQuery = q.Encode()

	resp, err := c.client.Get(u.String())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var out PeriodicReport
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}

	if out.Status != "000" { // 000: 정상
		return nil, fmt.Errorf("DART error %s: %s", out.Status, out.Message)
	}

	return out.List, nil
}

func New(apiKey string) *DartClient {
	return &DartClient{
		key: apiKey,
		client: &http.Client{
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{
					// DART는 TLS1.2 호환이 확실 — TLS1.2로 고정해서 협상 단순화
					MinVersion: tls.VersionTLS12,
					MaxVersion: tls.VersionTLS12,

					// SNI를 명시 (보통 자동이지만, 명시로 문제 회피)
					ServerName: "opendart.fss.or.kr",

					// 일부 구형 서버 대비 호환 암호군 지정 (필요 시)
					CipherSuites: []uint16{
						tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
						tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
						tls.TLS_RSA_WITH_AES_128_GCM_SHA256,
						tls.TLS_RSA_WITH_AES_256_GCM_SHA384,
					},
				},
			},
			Timeout: 20 * time.Second,
		},
	}
}

// only for testing
func (c *DartClient) UseDefaultClient() {
	c.client = http.DefaultClient
}
