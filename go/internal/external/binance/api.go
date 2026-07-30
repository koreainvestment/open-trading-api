package binance

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"slices"
	"strconv"
	"strings"
	"time"
)

const baseURL = "https://api.binance.com"

var allowedCryptos = []string{"BTC", "ETH", "SOL", "XRP", "APT", "POL"}
var client *http.Client

func GetCryptoRSI(crypto string) (float64, error) {
	if client == nil {
		client = &http.Client{
			Timeout: 20 * time.Second,
		}
	}

	if !slices.Contains(allowedCryptos, strings.ToUpper(crypto)) {
		return 0, fmt.Errorf("invalid crypto: %s", crypto)
	}

	symbol := fmt.Sprintf("%sUSDT", strings.ToUpper(crypto))
	url := fmt.Sprintf("%s/api/v3/klines?symbol=%s&interval=4h&limit=100", baseURL, symbol)
	resp, err := client.Get(url)
	if err != nil {
		log.Printf("Error fetching data: %v", err)
		return 0, err
	}
	defer resp.Body.Close()

	var klines [][]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&klines); err != nil {
		return 0, err
	}

	// 2. Parse Close Prices
	var closes []float64
	for _, k := range klines {
		// Binance API returns strings for prices, need to convert
		closePrice, err := strconv.ParseFloat(k[4].(string), 64)
		if err != nil {
			log.Printf("Invalid value from Binance. value: %v, error: %v", k[4], err)
			return 0, err
		}

		closes = append(closes, closePrice)
	}

	// 3. Calculate RSI
	rsi := CalculateRSI(closes, 14)
	log.Printf("Current %s 4h RSI: %.2f", crypto, rsi)

	if rsi <= 30 {
		log.Println("🚨 과매도 구간! 매수 고려 (Oversold)")
	} else if rsi >= 70 {
		log.Println("🔥 과매수 구간! 매도 고려 (Overbought)")
	} else {
		log.Println("⚖️ 중립 구간 (Neutral)")
	}

	return rsi, nil
}

// Simple RSI Calculation (Wilder's Smoothing)
func CalculateRSI(prices []float64, period int) float64 {
	if len(prices) < period+1 {
		return 0
	}

	var gains, losses float64

	// First Average Calculation
	for i := 1; i <= period; i++ {
		change := prices[i] - prices[i-1]
		if change > 0 {
			gains += change
		} else {
			losses -= change
		}
	}

	avgGain := gains / float64(period)
	avgLoss := losses / float64(period)

	// Smoothed Calculation for the rest
	for i := period + 1; i < len(prices); i++ {
		change := prices[i] - prices[i-1]
		var currentGain, currentLoss float64
		if change > 0 {
			currentGain = change
		} else {
			currentLoss = -change
		}

		avgGain = ((avgGain * float64(period-1)) + currentGain) / float64(period)
		avgLoss = ((avgLoss * float64(period-1)) + currentLoss) / float64(period)
	}

	if avgLoss == 0 {
		return 100
	}

	rs := avgGain / avgLoss
	return 100 - (100 / (1 + rs))
}
