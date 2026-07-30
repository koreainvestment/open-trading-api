package dataapi

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"time"
)

type DataAPIClient struct {
	key    string
	client *http.Client
}

type StockPriceResponse struct {
	Response struct {
		Header struct {
			ResultCode string `json:"resultCode"`
			ResultMsg  string `json:"resultMsg"`
		} `json:"header"`
		Body struct {
			NumOfRows  int `json:"numOfRows"`
			PageNo     int `json:"pageNo"`
			TotalCount int `json:"totalCount"`
			Items      struct {
				Item []struct {
					BasDt     string `json:"basDt"`
					SrtnCd    string `json:"srtnCd"`
					IsinCd    string `json:"isinCd"`
					ItmsNm    string `json:"itmsNm"`
					MrktCtg   string `json:"mrktCtg"`
					Clpr      string `json:"clpr"`
					Vs        string `json:"vs"`
					FltRt     string `json:"fltRt"`
					Mkp       string `json:"mkp"`
					Hipr      string `json:"hipr"`
					Lopr      string `json:"lopr"`
					Trqu      string `json:"trqu"`
					TrPrc     string `json:"trPrc"`
					LstgStCnt string `json:"lstgStCnt"`
					MktTotAmt string `json:"mktTotAmt"`
				} `json:"item"`
			} `json:"items"`
		} `json:"body"`
	} `json:"response"`
}

const baseURL = "https://apis.data.go.kr/"

// https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getDerivationProductMarketIndex?serviceKey=bfe5c7e2b2535ea6bf12d9357806a3009f1db1b1d159867359b8cc7e8ec6eb76&

func New(apiKey string) *DataAPIClient {
	return &DataAPIClient{
		key: apiKey,
		client: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

func (c *DataAPIClient) GetStockPrice(name string) (interface{}, error) {
	u, err := url.Parse(baseURL + "/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo")
	if err != nil {
		return nil, err
	}

	q := u.Query()
	q.Set("serviceKey", c.key) // API Key
	q.Set("numOfRows", "1")
	q.Set("pageNo", "1")
	q.Set("resultType", "json")
	q.Set("itmsNm", name)

	u.RawQuery = q.Encode()

	resp, err := c.client.Get(u.String())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// SECURITY: Stream JSON parsing to avoid Out Of Memory (OOM) vulnerabilities from io.ReadAll on large responses.
	var stockPriceResponse StockPriceResponse
	if err := json.NewDecoder(io.LimitReader(resp.Body, 100*1024*1024)).Decode(&stockPriceResponse); err != nil {
		log.Printf("failed to decode, err: %v, size: %v", err, resp.ContentLength)
		return nil, err
	}

	log.Printf("stockPriceResponse: %+v", stockPriceResponse)

	if stockPriceResponse.Response.Body.Items.Item == nil {
		return nil, fmt.Errorf("no stock price found")
	}

	return stockPriceResponse.Response.Body.Items.Item[0], nil
}
