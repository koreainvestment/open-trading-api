package main

import (
	"kosis/internal/pkg/binance"
	"kosis/internal/pkg/dataapi"
	"kosis/internal/pkg/fred"
	"log"
	"os"

	_ "github.com/joho/godotenv/autoload"
)

func main() {
	apiKey := os.Getenv("KOSIS_API_KEY")
	if apiKey == "" {
		log.Fatal("KOSIS_API_KEY is not set")
	}

	dartApiKey := os.Getenv("DART_API_KEY")
	if dartApiKey == "" {
		log.Fatal("DART_API_KEY is not set")
	}

	dataApiKey := os.Getenv("DATA_API_KEY")
	if dataApiKey == "" {
		log.Fatal("DATA_API_KEY is not set")
	}

	openaiApiKey := os.Getenv("OPENAI_API_KEY")
	if openaiApiKey == "" {
		log.Fatal("OPENAI_API_KEY is not set")
	}

	fredApiKey := os.Getenv("FRED_API_KEY")
	if fredApiKey == "" {
		log.Fatal("FRED_API_KEY is not set")
	}

	// kosisClient := kosis.New(apiKey)
	// if err := kosisClient.Search(); err != nil {
	// 	log.Fatalf("Failed to search KOSIS: %v", err)
	// }

	// dartClient := dart.New(dartApiKey)
	// reports, err := dartClient.GetRawReports()
	// if err != nil {
	// 	log.Fatalf("Failed to get raw reports: %v", err)
	// }

	rsi, err := binance.GetCryptoRSI("APT")
	if err != nil {
		log.Fatalf("Failed to get RSI: %v", err)
	}
	log.Printf("RSI: %f", rsi)

	fredClient := fred.New(fredApiKey)
	highYieldSpread, err := fredClient.GetHighYieldSpread()
	if err != nil {
		log.Fatalf("Failed to get high yield spread: %v", err)
	}
	log.Printf("High yield spread: %+v", highYieldSpread)

	dataapiClient := dataapi.New(dataApiKey)
	stockPrice, err := dataapiClient.GetStockPrice("삼성전자")
	if err != nil {
		log.Fatalf("Failed to get stock price: %v", err)
	}
	log.Printf("stockPrice: %+v", stockPrice)
}
