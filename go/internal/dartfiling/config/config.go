package config

import (
	"os"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL  string // Consolidated DB Connection URL
	RedisURL     string
	DartAPIKey   string
	KosisAPIKey  string
	OpenAIAPIKey string
	// Comma-separated origins, or exactly "*" for open CORS (no credentials). For credentialed CORS, list explicit origins only.
	AllowedOrigins string
}

// LoadConfig reads configuration from environment variables (.env file)
func LoadConfig() (*Config, error) {
	// Load .env file. In production, env variables are often set directly.
	if err := godotenv.Load(); err != nil {
		// Don't fail if .env is not present, just log it
		// log.Printf("Warning: .env file not found, reading from environment")
	}

	return &Config{
		DatabaseURL:    getEnv("DATABASE_URL", ""),
		RedisURL:       getEnv("REDIS_URL", ""),
		DartAPIKey:     getEnv("DART_API_KEY", ""),
		KosisAPIKey:    getEnv("KOSIS_API_KEY", ""),
		OpenAIAPIKey:   getEnv("OPENAI_API_KEY", ""),
		AllowedOrigins: getEnv("ALLOWED_ORIGINS", ""),
	}, nil
}

// Helper function to get env var or return default
func getEnv(key string, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
