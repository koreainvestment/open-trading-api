package testhelpers

import (
	"archive/zip"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
)

type Expectation struct {
	Method string
	URL    *url.URL

	StatusCode int
	RespBody   []byte
	Headers    http.Header

	isMatched      bool
	MismatchReason string
}

type MockTransport struct {
	Expectations []*Expectation
	mutex        sync.Mutex
}

func NewMockTransport() *MockTransport {
	return &MockTransport{
		Expectations: make([]*Expectation, 0),
	}
}

var (
	DefaultTransport                           = NewMockTransport()
	originalDefaultTransport http.RoundTripper = http.DefaultTransport
)

func New(baseURL string) *Expectation {
	u, err := url.Parse(baseURL)
	if err != nil {
		panic(fmt.Sprintf("gonock: invalid base URL provided: %v", err))
	}

	if u.Scheme == "" || u.Host == "" {
		panic(fmt.Sprintf("gonock: base URL must include scheme and host (e.g., http://%s)", baseURL))
	}

	exp := &Expectation{
		URL:     u,
		Headers: make(http.Header),
	}
	DefaultTransport.Add(exp)
	return exp
}

func (e *Expectation) Get(path string) *Expectation {
	e.Method = http.MethodGet

	u, err := url.Parse(path)
	if err != nil {
		panic(fmt.Sprintf("gonock: invalid path provided: %v", err))
	}

	e.URL.Path = u.Path
	e.URL.RawQuery = u.RawQuery
	return e
}

func (e *Expectation) Post(path string) *Expectation {
	e.Method = http.MethodPost
	e.URL.Path = path
	return e
}

func (e *Expectation) Reply(statusCode int) *Expectation {
	e.StatusCode = statusCode
	return e
}

func (e *Expectation) BodyString(body string) *Expectation {
	e.RespBody = []byte(body)
	return e
}

func (e *Expectation) Body(body []byte) *Expectation {
	e.RespBody = body
	return e
}

func (e *Expectation) JSON(v interface{}) *Expectation {
	data, err := json.Marshal(v)
	if err != nil {
		panic(fmt.Sprintf("gonock: failed to marshal JSON: %v", err))
	}
	e.RespBody = data
	e.Headers.Set("Content-Type", "application/json")
	return e
}

func (t *MockTransport) Add(exp *Expectation) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.Expectations = append(t.Expectations, exp)
}

func (t *MockTransport) Reset() {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.Expectations = make([]*Expectation, 0)
}

func IsDone() bool {
	DefaultTransport.mutex.Lock()
	defer DefaultTransport.mutex.Unlock()
	for _, exp := range DefaultTransport.Expectations {
		if !exp.isMatched {
			return false
		}
	}
	return true
}

func Activate() {
	if http.DefaultClient.Transport == DefaultTransport {
		return // Already active
	}

	if http.DefaultClient.Transport != nil {
		originalDefaultTransport = http.DefaultClient.Transport
	} else {
		originalDefaultTransport = http.DefaultTransport
	}

	http.DefaultClient.Transport = DefaultTransport
}

// Deactivate restores the original transport and resets all mocks.
func Deactivate() {
	http.DefaultClient.Transport = originalDefaultTransport
	DefaultTransport.Reset()
}

func (t *MockTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	t.mutex.Lock()
	defer t.mutex.Unlock()

	for _, exp := range t.Expectations {
		if !exp.isMatched && t.matches(exp, req) {
			exp.isMatched = true
			return t.buildResponse(exp, req), nil
		}
	}

	var reasons []string
	for _, exp := range t.Expectations {
		if exp.MismatchReason != "" {
			reasons = append(reasons, exp.MismatchReason)
		}
	}

	extra := ""
	if len(reasons) > 0 {
		extra = " (" + strings.Join(reasons, "; ") + ")"
	}

	return nil, fmt.Errorf("gonock: no match found for request %s %s%s", req.Method, req.URL, extra)
}

func (t *MockTransport) matches(exp *Expectation, req *http.Request) bool {
	exp.MismatchReason = ""

	if exp.Method != "" && exp.Method != req.Method {
		exp.MismatchReason = fmt.Sprintf("method mismatch: expected %s got %s", exp.Method, req.Method)
		return false
	}

	if exp.URL.Scheme != req.URL.Scheme {
		exp.MismatchReason = fmt.Sprintf("scheme mismatch: expected %s got %s", exp.URL.Scheme, req.URL.Scheme)
		return false
	}

	if exp.URL.Host != req.URL.Host {
		exp.MismatchReason = fmt.Sprintf("host mismatch: expected %s got %s", exp.URL.Host, req.URL.Host)
		return false
	}

	if exp.URL.Path != req.URL.Path {
		exp.MismatchReason = fmt.Sprintf("path mismatch: expected %s got %s", exp.URL.Path, req.URL.Path)
		return false
	}

	expectedQuery := exp.URL.Query()
	actualQuery := req.URL.Query()

	if len(expectedQuery) == 0 {
		return true
	}

	for key, values := range expectedQuery {
		actualValues, ok := actualQuery[key]
		if !ok {
			exp.MismatchReason = fmt.Sprintf("missing query key %s", key)
			return false
		}

		if len(actualValues) != len(values) {
			exp.MismatchReason = fmt.Sprintf("query value count mismatch for %s: expected %v got %v", key, values, actualValues)
			return false
		}

		for i, value := range values {
			if actualValues[i] != value {
				exp.MismatchReason = fmt.Sprintf("query mismatch for %s: expected %s got %s", key, value, actualValues[i])
				return false
			}
		}
	}

	return true
}

func (t *MockTransport) buildResponse(exp *Expectation, req *http.Request) *http.Response {
	statusCode := exp.StatusCode
	if statusCode == 0 {
		statusCode = http.StatusOK // Default to 200 OK if not specified
	}

	return &http.Response{
		StatusCode: statusCode,
		// Body must be an io.ReadCloser.
		Body:          io.NopCloser(bytes.NewReader(exp.RespBody)),
		Header:        exp.Headers,
		Request:       req,
		Proto:         "HTTP/1.1",
		ProtoMajor:    1,
		ProtoMinor:    1,
		ContentLength: int64(len(exp.RespBody)),
	}
}

func CreateMockZipArchive(filename string, data []byte) ([]byte, error) {
	buf := new(bytes.Buffer)

	zipWriter := zip.NewWriter(buf)

	var files = []struct {
		Name, Body string
	}{
		{filename, string(data)},
	}

	for _, file := range files {
		f, err := zipWriter.Create(file.Name)
		if err != nil {
			return nil, err
		}
		if _, err := f.Write([]byte(file.Body)); err != nil {
			return nil, err
		}
	}

	if err := zipWriter.Close(); err != nil {
		return nil, err
	}

	return buf.Bytes(), nil
}

func (e *Expectation) Header(key, value string) *Expectation {
	e.Headers.Set(key, value)
	return e
}
