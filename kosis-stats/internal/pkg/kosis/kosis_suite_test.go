package kosis

import (
	"testing"

	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestKosis(t *testing.T) {
	RegisterFailHandler(Fail)
	RunSpecs(t, "Kosis Suite")
}
