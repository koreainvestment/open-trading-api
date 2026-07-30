package models

import (
	"encoding/json"
	"time"
)

type ReportType struct {
	ID                uint `gorm:"primaryKey"`
	Name              string
	Structure         json.RawMessage `gorm:"type:jsonb"`
	SourceRawReportID uint
	CreatedAt         time.Time
	UpdatedAt         time.Time
}
