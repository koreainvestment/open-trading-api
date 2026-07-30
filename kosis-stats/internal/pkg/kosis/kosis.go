package kosis

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"net/url"
	"sort"
	"strconv"
	"strings"
	"time"
)

/*
parameters: https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList
table meta: https://kosis.kr/openapi/statisticsData.do?method=getMeta&type=TBL|ITM
search: https://kosis.kr/openapi/statisticsSearch.do?method=getList
*/

/*
	res: {
		"ORG_ID": "101",
		"ORG_NM": "통계청",
		"TBL_ID": "DT_1BPA001",
		"TBL_NM": "성 및 연령별 추계인구(1세별, 5세별) / 전국",
		"STAT_ID": "1994044",
		"STAT_NM": "장래인구추계",
		"VW_CD": "MT_ZTITLE",
		"MT_ATITLE": "인구 > 장래인구추계 > 전국(2022년 기준)",
		"FULL_PATH_ID": "A > A_6 > A41_10",
		"CONTENTS": "가정별 연령별 성별 추계인구 저위 추계(최소인구 추계: 출산율-저위 / 기대수명-저위 / 국제순이동-저위) 중위 추계(기본 추계: 출산율-중위 / 기대수명-중위 / 국제순이동-중위) 고위 추계(최대인구 추계: 출산율-고위 / 기대수명-고위 / 국제순이동-고위) 47세 48세 51세 55세 61세 62세 63세 71세 72세 75세 79세 80세 90 - 94세 8세 23세 29세 40세 45 - 49세 50 - 54세 60 - 64세 64세 65세 70 - 74세 78세 80 ...",
		"STRT_PRD_DE": "1960",
		"END_PRD_DE": "2072",
		"ITEM03": "주1) 2023년 12월에 공표한 장래인구추계 자료임. 주2) 매년 7월 1일 시점 자료임. 주3) 작성대상 인구는 국적과 상관없이 대한민국에 상주하는 인구임.(외국인 포함) 주4) 1960~2022년까지는 확정인구이며, 2023년 이후는 다음 인구추계시 변경될 수 있음. 주5) 중위추계(기본추계)는 인구변동요인별(출생, 사망, 국제이동) 중위가정을 조합한 결과, 고위추계(최대인구 추계)는 인구변동요인별(출생, 사망, 국제이동) 고위가정을 조합한 결과, 저위추계(최소인구 추계)는 인구변동요인별(출생, 사망, 국제이동) 저위가정을 조합한 결과임. 주6) 단위 : 명",
		"REC_TBL_SE": "N",
		"TBL_VIEW_URL": "https://kosis.kr/statisticsList/statisticsListIndex.do?menuId=M_01_01&vwcd=MT_ZTITLE&parmTabId=M_01_01&parentId=A.1;A_6.2;A41_10.3;",
		"LINK_URL": "http://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1BPA001",
		"STAT_DB_CNT": "102897",
		"QUERY": "인구"
	}

	err: {"err":"20","errMsg":"필수요청변수값이 누락되었습니다."}
*/

const baseURL = "https://kosis.kr/openapi"

type Client struct {
	key    string
	client *http.Client
}

type KosisSearchResponse struct {
	OrgID      string `json:"ORG_ID"`
	OrgNm      string `json:"ORG_NM"`
	TblID      string `json:"TBL_ID"`
	TblNm      string `json:"TBL_NM"`
	StatID     string `json:"STAT_ID"`
	StatNm     string `json:"STAT_NM"`
	VwCd       string `json:"VW_CD"`
	MtAtitle   string `json:"MT_ATITLE"`
	FullPathID string `json:"FULL_PATH_ID"`
	Contents   string `json:"CONTENTS"`
	StrtPrdDe  string `json:"STRT_PRD_DE"`
	EndPrdDe   string `json:"END_PRD_DE"`
	Item03     string `json:"ITEM03"`
	RecTblSe   string `json:"REC_TBL_SE"`
	TblViewURL string `json:"TBL_VIEW_URL"`
	LinkURL    string `json:"LINK_URL"`
	StatDbCnt  string `json:"STAT_DB_CNT"`
	Query      string `json:"QUERY"`
}

type KosisSearchErrorResponse struct {
	Err    string `json:"err"`
	ErrMsg string `json:"errMsg"`
}

func New(apiKey string) *Client {
	return &Client{
		key: apiKey,
		client: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

func (c *Client) get(path string, q url.Values, v any) error {
	if c.key == "" {
		return errors.New("missing KOSIS_API_KEY")
	}
	q.Set("apiKey", c.key)
	q.Set("format", "json")
	q.Set("jsonVD", "Y")

	u := fmt.Sprintf("%s/%s?%s", baseURL, path, q.Encode())
	log.Printf("u: %s", u)
	req, _ := http.NewRequest("GET", u, nil)
	resp, err := c.client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		b, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("kosis http %d: %s", resp.StatusCode, string(b))
	}

	return json.NewDecoder(resp.Body).Decode(v)
}

type TableRef struct {
	OrgID string
	TblID string
}

type MetaITM struct {
	ObjID    string `json:"OBJ_ID"`
	TblID    string `json:"TBL_ID"`
	OrgID    string `json:"ORG_ID"`
	ObjNM    string `json:"OBJ_NM"`
	ItmNM    string `json:"ITM_NM"`
	ItmID    string `json:"ITM_ID"`
	ObjIDSn  string `json:"OBJ_ID_SN"` // order index as string
	UnitNM   string `json:"UNIT_NM"`
	ObjNMEng string `json:"OBJ_NM_ENG"`
}

func (c *Client) GetMetaITM(ref TableRef) ([]MetaITM, error) {
	q := url.Values{}
	q.Set("method", "getMeta")
	q.Set("type", "ITM")
	q.Set("orgId", ref.OrgID)
	q.Set("tblId", ref.TblID)
	var data []MetaITM
	if err := c.get("statisticsData.do", q, &data); err != nil {
		return nil, err
	}
	return data, nil
}

type ParamRow struct {
	OrgID  string `json:"ORG_ID"`
	TblID  string `json:"TBL_ID"`
	TblNM  string `json:"TBL_NM"`
	ITMID  string `json:"ITM_ID"`
	ITMNM  string `json:"ITM_NM"`
	UnitNM string `json:"UNIT_NM"`
	PRDSE  string `json:"PRD_SE"`
	PRDDE  string `json:"PRD_DE"`
	DT     string `json:"DT"`

	C1   string `json:"C1"`
	C1NM string `json:"C1_NM"`
	C2   string `json:"C2"`
	C2NM string `json:"C2_NM"`
	// (C3..C8 필요시 확장)
}

func (c *Client) ParamData(ref TableRef, prdSe, start, end string, itmId string, obj map[int]string) ([]ParamRow, error) {
	q := url.Values{}
	q.Set("method", "getList")
	q.Set("orgId", ref.OrgID)
	q.Set("tblId", ref.TblID)
	q.Set("prdSe", prdSe)
	if start != "" {
		q.Set("startPrdDe", start)
	}
	if end != "" {
		q.Set("endPrdDe", end)
	}
	q.Set("itmId", itmId)
	for i := 1; i <= 8; i++ {
		if v, ok := obj[i]; ok && v != "" {
			q.Set(fmt.Sprintf("objL%d", i), v)
		}
	}
	var data []ParamRow
	if err := c.get("Param/statisticsParameterData.do", q, &data); err != nil {
		return nil, err
	}
	return data, nil
}

// --------- Meta helpers (공용) ---------

type ClassGroup struct {
	ObjID  string
	Name   string
	Order  int
	Values map[string]string // code -> label
}

type DigestedMeta struct {
	Items   map[string]string
	Classes []ClassGroup
}

func DigestITM(m []MetaITM) DigestedMeta {
	items := map[string]string{}
	tmp := map[string]*ClassGroup{}
	for _, r := range m {
		if r.ObjID == "ITEM" {
			items[strings.TrimSpace(r.ItmID)] = strings.TrimSpace(r.ItmNM)
			continue
		}
		if _, ok := tmp[r.ObjID]; !ok {
			order := 99
			if n, err := strconv.Atoi(strings.TrimSpace(r.ObjIDSn)); err == nil {
				order = n
			}
			tmp[r.ObjID] = &ClassGroup{ObjID: r.ObjID, Name: strings.TrimSpace(r.ObjNM), Order: order, Values: map[string]string{}}
		}
		tmp[r.ObjID].Values[strings.TrimSpace(r.ItmID)] = strings.TrimSpace(r.ItmNM)
	}
	out := make([]ClassGroup, 0, len(tmp))
	for _, g := range tmp {
		out = append(out, *g)
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Order < out[j].Order })
	return DigestedMeta{Items: items, Classes: out}
}

func FindItemIDByContains(items map[string]string, needle string) (string, bool) {
	for id, nm := range items {
		if strings.Contains(nm, needle) {
			return id, true
		}
	}
	return "", false
}

func FindClassIndexByName(classes []ClassGroup, keywords ...string) (int, bool) {
	for idx, g := range classes {
		for _, kw := range keywords {
			if strings.Contains(g.Name, kw) {
				return idx, true
			}
		}
	}
	return -1, false
}

func ParseNumber(s string) (float64, bool) {
	if s == "" || s == "-" {
		return math.NaN(), false
	}
	s = strings.ReplaceAll(s, ",", "")
	f, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return math.NaN(), false
	}
	return f, true
}

func (c *Client) Search() error {
	log.Printf("Starting KOSIS Stats")

	// example: https://kosis.kr/openapi/statisticsSearch.do?method=getList&apiKey=MThjYWY3MTRlYTllNjFlOTk4N2U2MzlkYmQ4OWVmYWI=&format=json&jsonVD=Y&searchNm=%EC%9D%B8%EA%B5%AC&startCount=1&resultCount=5&sort=RANK
	searchURL := "https://kosis.kr/openapi/statisticsSearch.do"

	method := "getList"
	format := "json"
	jsonVD := "Y"     // don't know what this is. hardcode it for now
	startCount := 1   // page number
	resultCount := 20 // limit per page
	sort := "RANK"    // RANK: 정확도순, DATE: 최신순
	searchNm := "인구"

	queryParams := url.Values{}
	queryParams.Add("method", method)
	queryParams.Add("format", format)
	queryParams.Add("jsonVD", jsonVD)
	queryParams.Add("apiKey", c.key)
	queryParams.Add("startCount", strconv.Itoa(startCount))
	queryParams.Add("resultCount", strconv.Itoa(resultCount))
	queryParams.Add("sort", sort)
	queryParams.Add("searchNm", searchNm)

	searchURL = fmt.Sprintf("%s?%s", searchURL, queryParams.Encode())

	searchRes := []*KosisSearchResponse{}

	err := c.makeRequest(searchURL, &searchRes)
	if err != nil {
		return err
	}

	for _, res := range searchRes {
		log.Printf("Response: %v", res.MtAtitle)
	}

	return nil
}

func (c *Client) makeRequest(url string, resBody interface{}) error {
	resp, err := c.client.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		errBody := &KosisSearchErrorResponse{}
		if err := json.NewDecoder(resp.Body).Decode(errBody); err != nil {
			return err
		}
		return fmt.Errorf("%s: %s", errBody.Err, errBody.ErrMsg)
	}

	return json.NewDecoder(resp.Body).Decode(resBody)
}
