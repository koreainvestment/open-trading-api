package tasks_test

import (
	"testing"

	"github.com/kis-open-api/go/internal/testhelpers"
	. "github.com/onsi/ginkgo/v2"
	. "github.com/onsi/gomega"
)

func TestTasks(t *testing.T) {
	t.Helper()
	RegisterFailHandler(Fail)
	RunSpecs(t, "Tasks Suite")
}

var _ = BeforeSuite(func() {
	testhelpers.LoadTestEnv()
})
