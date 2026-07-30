package models

import "time"

type Company struct {
	ID               uint `gorm:"primaryKey"`
	CorpCode         string
	CorpName         string
	CorpEngName      string
	LastModifiedDate time.Time
	Category         string // Y: Kospi, K: Kosdaq, N: Konex, E: etc
	CreatedAt        time.Time
	UpdatedAt        time.Time
}
