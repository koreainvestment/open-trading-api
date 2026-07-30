package main

import (
	"kosis/internal/config"
	"kosis/internal/pkg/dart"
	"kosis/internal/pkg/openai"
	"kosis/internal/tasks"
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
