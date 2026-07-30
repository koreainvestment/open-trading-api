package dart

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"kosis/internal/pkg/xbrl"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

const baseURL = "https://opendart.fss.or.kr/api"

type DartClient struct {
	key    string
	client *http.Client
}

type List struct {
	RceptNo  string `json:"rcept_no"`
	CorpCode string `json:"corp_code"`
	CorpName string `json:"corp_name"`
	ReportNm string `json:"report_nm"`
	RceptDt  string `json:"rcept_dt"`
	FlrNm    string `json:"flr_nm"`
	Rm       string `json:"rm"`
}

type ListResp struct {
	Status    string `json:"status"`
	Message   string `json:"message"`
	PageCnt   int    `json:"page_count"`
	Total     int    `json:"total_count"`
	PageNo    int    `json:"page_no"`
	TotalPage int    `json:"total_page"`
	List      []List `json:"list"`
}

type Company struct {
	CorpCode    string `xml:"corp_code"`
	CorpName    string `xml:"corp_name"`
	CorpEngName string `xml:"corp_eng_name"`
	ModifyDate  string `xml:"modify_date"`
}

type CorpCodeXML struct {
	XMLName   xml.Name  `xml:"result"`
	Companies []Company `xml:"list"`
}

type PageInfo struct {
	StartDate time.Time
	EndDate   time.Time
}

// defined error that document not found
var ErrDocumentNotFound = errors.New("document not found")

// 공시 목록 조회
// https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019001
func (c *DartClient) getDisclosureList(corpCode, bgnDe, endDe string, pageNo, pageCount int) (*ListResp, error) {
	u, _ := url.Parse(baseURL + "/list.json")
	q := u.Query()
	q.Set("crtfc_key", c.key) // API Key

	if corpCode != "" {
		q.Set("corp_code", corpCode) // 8자리 기업코드(예: 삼성전자 00126380)
	}
	if bgnDe != "" {
		q.Set("bgn_de", bgnDe) // YYYYMMDD, begin date, 3 months max
	}
	if endDe != "" {
		q.Set("end_de", endDe) // YYYYMMDD, end date
	}

	// page number, 1 by default
	if pageNo > 0 {
		q.Set("page_no", fmt.Sprint(pageNo))
	}

	// page count, 10 by default, max value is 100
	if pageCount > 0 {
		q.Set("page_count", fmt.Sprint(pageCount))
	}
	u.RawQuery = q.Encode()

	resp, err := c.client.Get(u.String())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var out ListResp

	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}

	if out.Status != "000" { // 000: 정상
		return nil, fmt.Errorf("DART error %s: %s", out.Status, out.Message)
	}

	return &out, nil
}

// 공시서류원본파일
// https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS001&apiId=2019003
func (c *DartClient) GetDocument(rceptNo string) (string, error) {
	u, _ := url.Parse(baseURL + "/document.xml")
	q := u.Query()
	q.Set("crtfc_key", c.key)  // API Key
	q.Set("rcept_no", rceptNo) // 접수번호

	u.RawQuery = q.Encode()

	resp, err := c.client.Get(u.String())
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	buf, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("DART error %d: %s", resp.StatusCode, string(buf))
	}

	// check if mime type is application/zip
	mimeType := resp.Header.Get("Content-Type")
	if mimeType == "application/xml;charset=UTF-8" {
		if strings.Contains(string(buf), "<status>014</status>") {
			return "", ErrDocumentNotFound
		}
		return string(buf), nil
	}

	zr, err := zip.NewReader(bytes.NewReader(buf), int64(len(buf)))
	if err != nil {
		return "", err
	}

	// SECURITY: Prevent Zip Bomb / memory exhaustion by limiting decompressed data to 100MB across all files
	if len(zr.File) > 100 {
		return "", fmt.Errorf("too many files in archive")
	}

	remainingBytes := int64(100 * 1024 * 1024)
	outBuf := new(bytes.Buffer)
	for _, f := range zr.File {
		rc, err := f.Open()
		if err != nil {
			return "", err
		}

		limitReader := io.LimitReader(rc, remainingBytes+1)
		copied, err := io.Copy(outBuf, limitReader)
		rc.Close()

		if copied > remainingBytes {
			return "", fmt.Errorf("decompressed data exceeds maximum allowed size")
		}
		if err != nil {
			return "", err
		}
		remainingBytes -= copied
	}

	return outBuf.String(), nil
}

func (c *DartClient) GetRecentRawReports(pageInfo ...PageInfo) ([]List, error) {
	code := ""
	size := 100
	page := 1

	var startDate string
	var endDate string

	if len(pageInfo) > 0 {
		startDate = pageInfo[0].StartDate.Format("20060102")
		endDate = pageInfo[0].EndDate.Format("20060102")
	} else {
		today := time.Now()
		startDate = today.AddDate(0, 0, -5).Format("20060102")
		endDate = today.Format("20060102")
	}

	log.Printf("Getting recent raw reports. Page: %d, Size: %d, StartDate: %s, EndDate: %s", page, size, startDate, endDate)

	res, err := c.getDisclosureList(code, startDate, endDate, page, size)
	if err != nil {
		return nil, err
	}

	for page < res.TotalPage {
		log.Printf("Getting next page of recent raw reports. Page: %d, Size: %d, StartDate: %s, EndDate: %s", page, size, startDate, endDate)

		page++
		nextPageRes, err := c.getDisclosureList(code, startDate, endDate, page, size)
		if err != nil {
			return nil, err
		}
		res.List = append(res.List, nextPageRes.List...)
	}

	return res.List, nil
}

func (c *DartClient) GetAllRawReports() ([]List, error) {
	return nil, fmt.Errorf("GetAllRawReports not implemented")
}

func (c *DartClient) GetCompanies() ([]Company, error) {
	fmt.Println("Getting companies")
	u, _ := url.Parse(baseURL + "/corpCode.xml")
	q := u.Query()
	q.Set("crtfc_key", c.key)
	u.RawQuery = q.Encode()
	resp, err := c.client.Get(u.String())
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	buf, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("DART error %d: %s", resp.StatusCode, string(buf))
	}

	zr, err := zip.NewReader(bytes.NewReader(buf), int64(len(buf)))
	if err != nil {
		return nil, err
	}

	// SECURITY: Prevent Zip Bomb / memory exhaustion by limiting decompressed data to 100MB across all files
	if len(zr.File) > 100 {
		return nil, fmt.Errorf("too many files in archive")
	}
	remainingBytes := int64(100 * 1024 * 1024)
	outBuf := new(bytes.Buffer)
	for _, f := range zr.File {
		rc, err := f.Open()
		if err != nil {
			return nil, err
		}

		limitReader := io.LimitReader(rc, remainingBytes+1)
		copied, err := io.Copy(outBuf, limitReader)
		rc.Close()

		if copied > remainingBytes {
			return nil, fmt.Errorf("decompressed data exceeds maximum allowed size")
		}
		if err != nil {
			return nil, err
		}
		remainingBytes -= copied
	}

	dec := xml.NewDecoder(bytes.NewReader(outBuf.Bytes()))
	var file CorpCodeXML

	if err := dec.Decode(&file); err != nil {
		return nil, err
	}

	// normalize a bit (optional but practical)
	for i := range file.Companies {
		c := &file.Companies[i]
		c.CorpCode = strings.TrimSpace(c.CorpCode)
		c.CorpName = strings.TrimSpace(c.CorpName)
		c.CorpEngName = strings.TrimSpace(c.CorpEngName)
		c.ModifyDate = strings.TrimSpace(c.ModifyDate)
	}

	return file.Companies, nil
}

func (c *DartClient) GetList() error {
	// 삼성전자(00126380) 2025-01-01 ~ 2025-01-31 공시 100건
	// LG화학(00356361) 2025-10-01 ~ 2025-10-31 공시 100건
	// 모든 회사 ""
	code := "00126380" // 00126380: 삼성전자, 00356361: LG화학, 01515323: LG에너지솔루션
	today := time.Now()
	startDate := today.AddDate(0, 0, -271).Format("20060102")
	endDate := today.AddDate(0, 0, -181).Format("20060102")
	res, err := c.getDisclosureList(code, startDate, endDate, 1, 100)
	if err != nil {
		return err
	}

	for _, it := range res.List {
		if err := c.processDoc(it); err != nil {
			if err == ErrDocumentNotFound {
				log.Printf("document not found: %s %s %s %s", it.RceptDt, it.RceptNo, it.CorpName, it.ReportNm)
				continue
			}

			return err
		}
	}

	return nil
}

// process doc
func (c *DartClient) processDoc(it List) error {
	folder := fmt.Sprintf("data/receipts/%s", it.CorpCode)
	filename := fmt.Sprintf("%s/%s.html", folder, it.RceptNo)

	// a file exists, skip and read the file
	doc := ""
	if _, err := os.Stat(filename); err == nil {
		b, err := os.ReadFile(filename)
		if err != nil {
			return err
		}

		doc = string(b)
	} else {
		// create a folder if not exists
		if _, err := os.Stat(folder); err != nil {
			if err := os.MkdirAll(folder, 0755); err != nil {
				return err
			}
		}

		doc, err = c.GetDocument(it.RceptNo)
		if err != nil {
			return err
		}

		f, err := os.Create(filename)
		if err != nil {
			return err
		}
		defer f.Close()

		_, err = f.WriteString(doc)
		if err != nil {
			return err
		}
	}

	fmt.Printf("%s %s %s %s %d\n", it.RceptDt, it.RceptNo, it.CorpName, it.ReportNm, len(doc))

	return StoreFiles([]byte(doc), it.CorpCode)
}

// store file in compact and markdown folders
func StoreFiles(rawReport []byte, corpCode string) error {
	report, err := xbrl.ParseXBRL(rawReport)
	if err != nil {
		return err
	}

	j, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}

	compactFolder := fmt.Sprintf("data/compact/%s", corpCode)

	if _, err := os.Stat(compactFolder); err != nil {
		if err := os.MkdirAll(compactFolder, 0755); err != nil {
			return err
		}
	}

	compactFilename := fmt.Sprintf("%s/%s.json", compactFolder, corpCode)
	if err := os.WriteFile(compactFilename, j, 0644); err != nil {
		return err
	}

	markdownFolder := fmt.Sprintf("data/markdowns/%s", corpCode)
	if _, err := os.Stat(markdownFolder); err != nil {
		if err := os.MkdirAll(markdownFolder, 0755); err != nil {
			return err
		}
	}

	markdownFilename := fmt.Sprintf("%s/%s.md", markdownFolder, corpCode)
	return os.WriteFile(markdownFilename, []byte(xbrl.ReportToMarkdown(report)), 0644)
}
