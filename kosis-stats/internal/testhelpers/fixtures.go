package testhelpers

import (
	"os"
	"path/filepath"
)

func LoadFixture(name string) ([]byte, error) {
	filepath := filepath.Join("..", "testhelpers", "fixtures", name)
	return os.ReadFile(filepath)
}
