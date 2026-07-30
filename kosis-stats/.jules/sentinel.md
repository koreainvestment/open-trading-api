## 2024-05-18 - [Overly Permissive CORS Configuration]

**Vulnerability:** The API allowed `Access-Control-Allow-Origin: *` while simultaneously setting `Access-Control-Allow-Credentials: true`. This combination is a security risk as it allows any origin to make authenticated cross-origin requests using the user's credentials, potentially exposing sensitive data.
**Learning:** Hardcoding `*` for allowed origins alongside credentials allows for CSRF-like attacks where a malicious site can read responses using a user's session.
**Prevention:** Implement a dynamic origin validation mechanism that checks incoming origins against an explicit, configurable allowlist before setting the `Access-Control-Allow-Origin` and `Access-Control-Allow-Credentials` headers.

## 2026-03-13 - [Wildcard CORS + reflect Origin + credentials]

**Vulnerability:** Treating `ALLOWED_ORIGINS=*` by reflecting the request `Origin` and setting `Access-Control-Allow-Credentials: true` is worse than `*` + credentials (browsers reject the latter). Reflected origin + credentials is accepted, so any site could perform credentialed cross-origin requests.
**Prevention:** If open CORS is required, use literal `Access-Control-Allow-Origin: *` and omit `Access-Control-Allow-Credentials`. For cookies/auth cross-origin, use an explicit origin allowlist and reflect only listed origins.

## 2026-03-21 - [Pagination Limit DoS/OOM Vulnerability]

**Vulnerability:** The application used a query parameter to dynamically set database limits in `getLimitWithDefault()`, but did not validate that the limit was strictly positive and adequately bounded. GORM treats a negative limit (like `-1`) as "no limit", which an attacker could use to bypass pagination and fetch an excessively large dataset into memory, causing Denial of Service (DoS) or Out of Memory (OOM) errors.
**Learning:** Object Relational Mappers (ORMs) like GORM have specific behaviors regarding default or special numeric arguments. In this case, passing negative values disables limits. It highlights the importance of not just capping the maximum value, but verifying lower bounds.
**Prevention:** Always ensure pagination limit parameters are explicitly bounded to a strictly positive range (e.g., `0 < limit <= MAX_LIMIT`) before passing them to ORMs or database engines.

## 2026-06-29 - [Missing HTTP Timeout in API Clients]

**Vulnerability:** External HTTP API requests (e.g., to FRED, Binance) used the default `http.Get` function without an explicit timeout configured.
**Learning:** The default package-level `http.Get`, `http.Post`, etc., do not enforce any timeouts. If the external server hangs or responds very slowly, the connection will remain open indefinitely. In a concurrent environment, this can lead to thread/goroutine exhaustion, file descriptor limits being reached, and ultimately a Denial of Service (DoS) of the application.
**Prevention:** Always use a custom instantiated `http.Client` with a strictly defined `Timeout` property (e.g., `&http.Client{Timeout: 10 * time.Second}`) when interacting with external networks. Avoid the default `http` package convenience functions.

## 2024-05-24 - [Zip Bomb Vulnerability in DART Archive Extraction]
**Vulnerability:** The application unzipped files directly into memory without bounding the aggregate size of decompressed data across the archive. This made it vulnerable to decompression bomb (Zip Bomb) attacks leading to memory exhaustion (OOM) or Denial of Service (DoS).
**Learning:** Even when processing data from seemingly trusted third-party APIs like DART, we must assume the input data format could be malformed or exploited. Decompressing archives without tracking the cumulative bytes read is dangerous.
**Prevention:** Always use `io.LimitReader` and track the total bytes decompressed against a strict limit (e.g., 100MB) when extracting archives, returning an error if the limit is exceeded.

## 2024-05-18 - [DoS Vulnerability in Default HTTP Client]

**Vulnerability:** Usage of the default `http.Get` which implicitly uses `http.DefaultClient`. The default client lacks a timeout. If the external server hangs, connections can stay open indefinitely leading to goroutine leaks and resource exhaustion (DoS).
**Learning:** Default HTTP clients in Go are unsuitable for production code when interacting with external networks. Timeouts must always be explicitly configured.
**Prevention:** Always instantiate a custom `http.Client` with an explicit `Timeout` (e.g., `client := &http.Client{Timeout: 10 * time.Second}`) instead of relying on package-level HTTP functions.
