package fred

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"time"
)

const baseURL = "https://api.stlouisfed.org"

type FREDClient struct {
	apiKey string
	client *http.Client
}

type HighYieldSpreadResponse struct {
	RealtimeStart    string `json:"realtime_start"`
	RealtimeEnd      string `json:"realtime_end"`
	ObservationStart string `json:"observation_start"`
	ObservationEnd   string `json:"observation_end"`
	Units            string `json:"units"`
	OutputType       int    `json:"output_type"`
	FileType         string `json:"file_type"`
	OrderBy          string `json:"order_by"`
	SortOrder        string `json:"sort_order"`
	Count            int    `json:"count"`
	Offset           int    `json:"offset"`
	Limit            int    `json:"limit"`
	Observations     []struct {
		RealtimeStart string `json:"realtime_start"`
		RealtimeEnd   string `json:"realtime_end"`
		Date          string `json:"date"`
		Value         string `json:"value"`
	} `json:"observations"`
}

func New(apiKey string) *FREDClient {
	return &FREDClient{
		apiKey: apiKey,
		client: &http.Client{
			Timeout: 20 * time.Second,
		},
	}
}

func (c *FREDClient) GetHighYieldSpread() (map[string]float64, error) {
	if c.client == nil {
		return nil, errors.New("Client not initialized")
	}

	url := fmt.Sprintf("%s/fred/series/observations?series_id=BAMLH0A0HYM2&api_key=%s&file_type=json", baseURL, c.apiKey)
	// SECURITY: Use custom client with explicit timeout to prevent DoS (resource exhaustion) if the external API hangs.
	resp, err := c.client.Get(url)
	if err != nil {
		log.Printf("Error fetching data: %v", err)
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	res := &HighYieldSpreadResponse{}

	if err := json.Unmarshal(body, &res); err != nil {
		return nil, err
	}

	result := map[string]float64{}
	for _, observation := range res.Observations {
		if observation.Value == "." {
			continue
		}

		v, err := strconv.ParseFloat(observation.Value, 64)
		if err != nil {
			log.Printf("Invalid value from FRED. value: %v, error: %v", observation.Value, err)
			return nil, err
		}
		result[observation.Date] = v
	}

	return result, nil
}
