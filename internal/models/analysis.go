package models

import (
	"encoding/json"
	"time"
)

type Analysis struct {
	ID          uint `gorm:"primaryKey"`
	RawReportID uint
	UsedTokens  int64
	Analysis    json.RawMessage `gorm:"type:jsonb"`
	CreatedAt   time.Time
	UpdatedAt   time.Time
}
