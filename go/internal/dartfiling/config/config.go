package config

import (
	"os"

	"github.com/joho/godotenv"
)

// Config holds all configuration for the application
type Config struct {
	DatabaseURL    string // Consolidated DB Connection URL
	RedisURL       string
	DartAPIKey     string
	KosisAPIKey    string
	OpenAIAPIKey   string
	AllowedOrigins string
}

// LoadConfig reads configuration from environment variables (.env file)
func LoadConfig() (*Config, error) {
	_ = godotenv.Load()

	return &Config{
		DatabaseURL:    getEnv("DATABASE_URL", "postgresql://sunjinlee@127.0.0.1:5432/dart?sslmode=disable"),
		RedisURL:       getEnv("REDIS_URL", "redis://127.0.0.1:6379/0"),
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
