package main

import (
	"context"
	"log"
	"os"
	"strconv"

	"github.com/kis-open-api/go/internal/dartfiling/config"
	"github.com/kis-open-api/go/internal/dartfiling/tasks"
	"github.com/kis-open-api/go/internal/db"
	"github.com/kis-open-api/go/internal/external/dart"
	"github.com/kis-open-api/go/internal/external/openai"
)

func fatalUsage() {
	log.Fatalf("Usage:\n"+
		"  %s companies                     (backfill companies into DB)\n"+
		"  %s company <corp_code> [limit]   (fetch disclosures for a specific company into DB)\n"+
		"  %s reports [corp_code] [limit]   (fetch recent disclosures into DB)\n"+
		"  %s dry-run <receipt_number>      (dry-run single disclosure analysis without DB)\n"+
		"  %s <receipt_number>              (dry-run single disclosure analysis without DB)",
		os.Args[0], os.Args[0], os.Args[0], os.Args[0], os.Args[0])
}

// DART receipt numbers are 14 digits: YYYYMMDD + 1 type digit + 5 sequence digits.
func isReceiptNumber(s string) bool {
	if len(s) != 14 {
		return false
	}
	for _, r := range s {
		if r < '0' || r > '9' {
			return false
		}
	}
	return true
}

func main() {
	if len(os.Args) < 2 {
		fatalUsage()
	}

	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	subcommand := os.Args[1]

	switch subcommand {
	case "companies", "backfill-companies", "sync-companies":
		dbConn, err := db.InitDB(cfg.DatabaseURL)
		if err != nil {
			log.Fatalf("Failed to connect to database: %v", err)
		}
		processor := tasks.NewTaskProcessor(dbConn, cfg)

		task, err := tasks.NewFetchCompaniesTask()
		if err != nil {
			log.Fatalf("Failed to create fetch companies task: %v", err)
		}

		ctx := context.Background()
		log.Println("Starting backfill for companies...")
		if err := processor.HandleFetchCompaniesTask(ctx, task); err != nil {
			log.Fatalf("Failed to backfill companies: %v", err)
		}
		log.Println("Companies backfill complete.")

	case "company", "reports", "fetch-reports":
		requireCorpCode := subcommand == "company"
		if requireCorpCode && len(os.Args) < 3 {
			log.Fatalf("Usage: %s company <corp_code> [limit]", os.Args[0])
		}

		var corpCode *string
		var limit *int
		if len(os.Args) >= 3 {
			code := os.Args[2]
			corpCode = &code
		}
		if len(os.Args) >= 4 {
			l, err := strconv.Atoi(os.Args[3])
			if err != nil || l <= 0 {
				log.Fatalf("invalid limit %q: must be a positive integer", os.Args[3])
			}
			limit = &l
		}

		dbConn, err := db.InitDB(cfg.DatabaseURL)
		if err != nil {
			log.Fatalf("Failed to connect to database: %v", err)
		}
		processor := tasks.NewTaskProcessor(dbConn, cfg)

		task, err := tasks.NewFetchReportsTask(corpCode, limit)
		if err != nil {
			log.Fatalf("Failed to create fetch reports task: %v", err)
		}

		ctx := context.Background()
		if corpCode != nil && limit != nil {
			log.Printf("Starting report fetch for company corp_code=%s (limit=%d)...", *corpCode, *limit)
		} else if corpCode != nil {
			log.Printf("Starting report fetch for company corp_code=%s...", *corpCode)
		} else if limit != nil {
			log.Printf("Starting report fetch for all recent disclosures (limit=%d)...", *limit)
		} else {
			log.Println("Starting report fetch for all recent disclosures...")
		}

		if err := processor.HandleFetchReportsTask(ctx, task); err != nil {
			log.Fatalf("Failed to fetch reports: %v", err)
		}
		log.Println("Report fetch complete.")

	case "dry-run":
		if len(os.Args) < 3 {
			log.Fatalf("Usage: %s dry-run <receipt_number>", os.Args[0])
		}
		receiptNumber := os.Args[2]
		runDryRun(cfg, receiptNumber)

	default:
		// Fallback for single receipt_number argument
		if !isReceiptNumber(subcommand) {
			log.Printf("unknown command: %q", subcommand)
			fatalUsage()
		}
		runDryRun(cfg, subcommand)
	}
}

func runDryRun(cfg *config.Config, receiptNumber string) {
	dartClient := dart.New(cfg.DartAPIKey)
	fileAnalyzer := openai.NewFileAnalyzer(cfg.OpenAIAPIKey)

	log.Printf("Running dry-run analysis for receipt_number=%s...", receiptNumber)
	err := tasks.FetchReportDryRun(dartClient, fileAnalyzer, receiptNumber)
	if err != nil {
		log.Fatalf("Failed to fetch report dry-run: %v", err)
	}
	log.Println("Dry-run complete.")
}
