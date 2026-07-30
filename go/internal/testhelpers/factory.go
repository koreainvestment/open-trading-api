package testhelpers

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/joho/godotenv"
	g "github.com/onsi/gomega"
	"gorm.io/gorm"
)

func LoadTestEnv() {
	dir, err := os.Getwd()
	if err != nil {
		return
	}
	for {
		testEnvPath := filepath.Join(dir, ".env.test")
		if _, err := os.Stat(testEnvPath); err == nil {
			_ = godotenv.Overload(testEnvPath)
			return
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			break
		}
		dir = parent
	}
}

func CleanupDB(db *gorm.DB) {
	var dbName string
	if err := db.Raw("SELECT current_database()").Scan(&dbName).Error; err != nil {
		panic(fmt.Sprintf("failed to get current database name: %v", err))
	}

	// if database name is not end with _test, panic
	if !strings.HasSuffix(dbName, "_test") {
		panic(fmt.Sprintf("database name '%s' does not end with _test, skipping cleanup to prevent data loss", dbName))
	}

	var tables []string

	err := db.Raw("SELECT tablename FROM pg_tables WHERE schemaname = 'public'").Scan(&tables).Error
	g.Expect(err).NotTo(g.HaveOccurred())

	if len(tables) == 0 {
		return
	}

	for _, table := range tables {
		if table == "spatial_ref_sys" || table == "schema_migrations" {
			continue
		}

		query := fmt.Sprintf("TRUNCATE TABLE \"%s\" RESTART IDENTITY CASCADE", table)
		err := db.Exec(query).Error
		g.Expect(err).NotTo(g.HaveOccurred(), "Failed to truncate table: "+table)
	}
}
