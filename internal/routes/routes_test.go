package routes

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"gorm.io/gorm"
	"kosis/internal/config"
)

func TestCORS(t *testing.T) {
	// Create a mock DB and config
	db := &gorm.DB{}
	cfg := &config.Config{
		AllowedOrigins: "http://localhost:3000, https://example.com ",
	}

	router := SetupRouter(db, cfg)

	tests := []struct {
		name           string
		origin         string
		expectedStatus int
		expectedOrigin string
	}{
		{
			name:           "Allowed Origin",
			origin:         "http://localhost:3000",
			expectedStatus: http.StatusOK,
			expectedOrigin: "http://localhost:3000",
		},
		{
			name:           "Another Allowed Origin with whitespace in config",
			origin:         "https://example.com",
			expectedStatus: http.StatusOK,
			expectedOrigin: "https://example.com",
		},
		{
			name:           "Disallowed Origin",
			origin:         "http://malicious.com",
			expectedStatus: http.StatusOK,
			expectedOrigin: "", // Should not be set
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req, _ := http.NewRequest("GET", "/health", nil)
			if tc.origin != "" {
				req.Header.Set("Origin", tc.origin)
			}
			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)

			if w.Code != tc.expectedStatus {
				t.Errorf("Expected status %d, got %d", tc.expectedStatus, w.Code)
			}

			originHeader := w.Header().Get("Access-Control-Allow-Origin")
			if originHeader != tc.expectedOrigin {
				t.Errorf("Expected Origin %q, got %q", tc.expectedOrigin, originHeader)
			}
			if tc.expectedOrigin != "" {
				if w.Header().Get("Access-Control-Allow-Credentials") != "true" {
					t.Errorf("allowlisted origin should set Allow-Credentials true")
				}
			}
			if w.Header().Get("Vary") != "Origin" {
				t.Errorf("allowlist CORS must set Vary: Origin for cache safety; got %q", w.Header().Get("Vary"))
			}
		})
	}
}

func TestCORSWildcard(t *testing.T) {
	db := &gorm.DB{}
	cfg := &config.Config{AllowedOrigins: "*"}
	router := SetupRouter(db, cfg)

	req, _ := http.NewRequest("GET", "/health", nil)
	req.Header.Set("Origin", "http://malicious.com")

	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status 200, got %d", w.Code)
	}
	// Wildcard must be literal * without credentials — never reflect attacker Origin + credentials
	if got := w.Header().Get("Access-Control-Allow-Origin"); got != "*" {
		t.Errorf("Expected Access-Control-Allow-Origin %q, got %q", "*", got)
	}
	if got := w.Header().Get("Access-Control-Allow-Credentials"); got != "" {
		t.Errorf("wildcard open CORS must not send Allow-Credentials; got %q", got)
	}
	// Literal * is same for every request; Vary: Origin not required for CORS caching
	if got := w.Header().Get("Vary"); got != "" {
		t.Errorf("wildcard CORS should not require Vary: Origin; got %q", got)
	}
}
