package testhelpers

import (
	"os"
	"path/filepath"
)

func LoadFixture(name string) ([]byte, error) {
	paths := []string{
		filepath.Join("..", "testhelpers", "fixtures", name),
		filepath.Join("..", "..", "testhelpers", "fixtures", name),
		filepath.Join("fixtures", name),
	}
	for _, p := range paths {
		if data, err := os.ReadFile(p); err == nil {
			return data, nil
		}
	}
	return os.ReadFile(filepath.Join("..", "..", "testhelpers", "fixtures", name))
}
