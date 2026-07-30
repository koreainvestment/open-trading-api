package kosis

import (
	"encoding/json"
	"math"
	"net/http"
	"net/http/httptest"
	"net/url"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

var _ = Describe("KosisClient", func() {
	var (
		client *Client
		apiKey = "test-key"
	)

	BeforeEach(func() {
		client = New(apiKey)
	})

	Describe("makeRequest", func() {
		BeforeEach(func() {
			client.client.Transport = roundTripperFunc(func(req *http.Request) (*http.Response, error) {
				w := httptest.NewRecorder()
				if req.URL.Path == "/success" {
					w.WriteHeader(http.StatusOK)
					json.NewEncoder(w).Encode([]*KosisSearchResponse{{OrgID: "101", OrgNm: "Test Org"}})
				} else if req.URL.Path == "/error" {
					w.WriteHeader(http.StatusBadRequest)
					json.NewEncoder(w).Encode(KosisSearchErrorResponse{Err: "400", ErrMsg: "Bad Request"})
				} else if req.URL.Path == "/invalid-json" {
					w.WriteHeader(http.StatusOK)
					w.Write([]byte("invalid json"))
				} else {
					w.WriteHeader(http.StatusNotFound)
				}
				return w.Result(), nil
			})
		})

		It("handles successful requests", func() {
			var res []*KosisSearchResponse
			err := client.makeRequest("http://localhost/success", &res)
			Expect(err).NotTo(HaveOccurred())
			Expect(res).To(HaveLen(1))
			Expect(res[0].OrgNm).To(Equal("Test Org"))
		})

		It("handles error responses from server", func() {
			var res []*KosisSearchResponse
			err := client.makeRequest("http://localhost/error", &res)
			Expect(err).To(HaveOccurred())
			Expect(err.Error()).To(Equal("400: Bad Request"))
		})

		It("handles invalid JSON responses", func() {
			var res []*KosisSearchResponse
			err := client.makeRequest("http://localhost/invalid-json", &res)
			Expect(err).To(HaveOccurred())
		})
	})

	Describe("get", func() {
		BeforeEach(func() {
			client.client.Transport = roundTripperFunc(func(req *http.Request) (*http.Response, error) {
				w := httptest.NewRecorder()
				if req.URL.Path == "/openapi/test-path" {
					w.WriteHeader(http.StatusOK)
					json.NewEncoder(w).Encode([]MetaITM{{ObjID: "ITEM", ItmNM: "Test Item"}})
				} else {
					w.WriteHeader(http.StatusNotFound)
				}
				return w.Result(), nil
			})
		})

		It("handles successful get requests", func() {
			var data []MetaITM
			err := client.get("test-path", url.Values{}, &data)
			Expect(err).NotTo(HaveOccurred())
			Expect(data).To(HaveLen(1))
			Expect(data[0].ItmNM).To(Equal("Test Item"))
		})

		It("handles errors on get requests", func() {
			client.client.Transport = roundTripperFunc(func(req *http.Request) (*http.Response, error) {
				w := httptest.NewRecorder()
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte("internal server error"))
				return w.Result(), nil
			})

			var data []MetaITM
			err := client.get("test-path", url.Values{}, &data)
			Expect(err).To(HaveOccurred())
			Expect(err.Error()).To(Equal("kosis http 500: internal server error"))
		})
	})
})

var _ = Describe("Kosis Helpers", func() {
	Describe("ParseNumber", func() {
		It("parses empty string as NaN", func() {
			val, ok := ParseNumber("")
			Expect(ok).To(BeFalse())
			Expect(math.IsNaN(val)).To(BeTrue())
		})

		It("parses hyphen as NaN", func() {
			val, ok := ParseNumber("-")
			Expect(ok).To(BeFalse())
			Expect(math.IsNaN(val)).To(BeTrue())
		})

		It("parses clean numbers", func() {
			val, ok := ParseNumber("1234.56")
			Expect(ok).To(BeTrue())
			Expect(val).To(Equal(1234.56))
		})

		It("parses numbers with commas", func() {
			val, ok := ParseNumber("1,234,567.89")
			Expect(ok).To(BeTrue())
			Expect(val).To(Equal(1234567.89))
		})

		It("fails on invalid strings", func() {
			val, ok := ParseNumber("abc")
			Expect(ok).To(BeFalse())
			Expect(math.IsNaN(val)).To(BeTrue())
		})
	})

	Describe("FindItemIDByContains", func() {
		var items map[string]string

		BeforeEach(func() {
			items = map[string]string{
				"1": "인구수",
				"2": "출생아수",
				"3": "사망률",
			}
		})

		It("finds matching item ID when it exists", func() {
			id, found := FindItemIDByContains(items, "출생")
			Expect(found).To(BeTrue())
			Expect(id).To(Equal("2"))
		})

		It("returns false when item does not exist", func() {
			_, found := FindItemIDByContains(items, "결혼")
			Expect(found).To(BeFalse())
		})
	})

	Describe("FindClassIndexByName", func() {
		var classes []ClassGroup

		BeforeEach(func() {
			classes = []ClassGroup{
				{ObjID: "C1", Name: "행정구역별"},
				{ObjID: "C2", Name: "연령별"},
				{ObjID: "C3", Name: "성별"},
			}
		})

		It("finds correct index matching a keyword", func() {
			idx, found := FindClassIndexByName(classes, "연령")
			Expect(found).To(BeTrue())
			Expect(idx).To(Equal(1))
		})

		It("finds correct index matching any of the keywords", func() {
			idx, found := FindClassIndexByName(classes, "남자", "성별")
			Expect(found).To(BeTrue())
			Expect(idx).To(Equal(2))
		})

		It("returns false when no keyword matches", func() {
			_, found := FindClassIndexByName(classes, "직업")
			Expect(found).To(BeFalse())
		})
	})

	Describe("DigestITM", func() {
		It("digests MetaITM slices into DigestedMeta correctly", func() {
			metaList := []MetaITM{
				{ObjID: "ITEM", ItmID: "100", ItmNM: "인구수"},
				{ObjID: "C1", ItmID: "00", ItmNM: "전국", ObjNM: "행정구역별", ObjIDSn: "1"},
				{ObjID: "C2", ItmID: "M", ItmNM: "남자", ObjNM: "성별", ObjIDSn: "2"},
				{ObjID: "C2", ItmID: "F", ItmNM: "여자", ObjNM: "성별", ObjIDSn: "2"},
			}

			digested := DigestITM(metaList)

			// Verify items
			Expect(digested.Items).To(HaveKeyWithValue("100", "인구수"))

			// Verify class groups
			Expect(digested.Classes).To(HaveLen(2))

			// Verify sorting order
			Expect(digested.Classes[0].ObjID).To(Equal("C1"))
			Expect(digested.Classes[0].Name).To(Equal("행정구역별"))
			Expect(digested.Classes[0].Values).To(HaveKeyWithValue("00", "전국"))

			Expect(digested.Classes[1].ObjID).To(Equal("C2"))
			Expect(digested.Classes[1].Name).To(Equal("성별"))
			Expect(digested.Classes[1].Values).To(HaveKeyWithValue("M", "남자"))
			Expect(digested.Classes[1].Values).To(HaveKeyWithValue("F", "여자"))
		})
	})
})

type roundTripperFunc func(*http.Request) (*http.Response, error)

func (f roundTripperFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req)
}
