package models

import (
	"encoding/json"
	"time"
)

type RawReport struct {
	ID            uint `gorm:"primaryKey"`
	ReceiptNumber string
	CorpCode      string
	ReportName    string
	BlobData      []byte
	BlobSize      int
	JSONData      json.RawMessage `gorm:"type:jsonb"`
	CreatedAt     time.Time
	UpdatedAt     time.Time
}
