package main

import (
	"github.com/kis-open-api/go/internal/dartfiling/config"
	"github.com/kis-open-api/go/internal/external/dart"
	"github.com/kis-open-api/go/internal/external/openai"
	"github.com/kis-open-api/go/internal/dartfiling/tasks"
	"log"
	"os"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	if len(os.Args) != 2 {
		log.Fatalf("Usage: %s <receipt_number>", os.Args[0])
	}

	dartClient := dart.New(cfg.DartAPIKey)
	fileAnalyzer := openai.NewFileAnalyzer(cfg.OpenAIAPIKey)

	receiptNumber := os.Args[1]
	err = tasks.FetchReportDryRun(dartClient, fileAnalyzer, receiptNumber)
	if err != nil {
		log.Fatalf("Failed to fetch report: %v", err)
	}

	log.Println("Done")
}
