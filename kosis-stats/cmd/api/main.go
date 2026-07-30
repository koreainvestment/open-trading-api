package main

import (
	"fmt"
	"kosis/internal/config"
	"kosis/internal/db"
	"kosis/internal/routes"
	"log"

	_ "github.com/joho/godotenv/autoload"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	db, err := db.InitDB(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	var result map[string]interface{}
	if err := db.Raw("SELECT 1").Scan(&result).Error; err != nil {
		log.Fatalf("Failed to check database connection: %v", err)
	}

	router := routes.SetupRouter(db, cfg)

	serverAddr := fmt.Sprintf(":%s", "8080")
	log.Printf("Starting server on %s", serverAddr)
	if err := router.Run(serverAddr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
