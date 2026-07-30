package xbrl

import (
	"fmt"
	"strings"

	"github.com/PuerkitoBio/goquery"
	"golang.org/x/net/html"
)

func ParseXBRL(raw []byte) (*UsefulReport, error) {
	rawString := string(raw)
	rawString = strings.ReplaceAll(rawString, "<TU", "<TD")
	rawString = strings.ReplaceAll(rawString, "</TU>", "</TD>")
	rawString = strings.ReplaceAll(rawString, "<TE", "<TD")
	rawString = strings.ReplaceAll(rawString, "</TE>", "</TD>")

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(rawString))
	if err != nil {
		return nil, err
	}

	report := &UsefulReport{}
	report.ReportTitle = doc.Find("DOCUMENT-NAME").First().Text()
	companyNameSelection := doc.Find("COMPANY-NAME").First()
	report.CompanyName = companyNameSelection.Text()
	companyCIK, exists := companyNameSelection.Attr("aregcik")
	if exists {
		report.CompanyCIK = companyCIK
	} else {
		report.CompanyCIK = ""
	}

	var tables [][][]string
	doc.Find("TABLE").Each(func(i int, table *goquery.Selection) {
		rows := [][]string{}
		table.Find("TR").Each(func(i int, row *goquery.Selection) {
			cells := []string{}

			row.Children().Each(func(i int, s *goquery.Selection) {
				tag := goquery.NodeName(s)
				if strings.EqualFold(tag, "td") || strings.EqualFold(tag, "th") || strings.EqualFold(tag, "tu") || strings.EqualFold(tag, "te") {
					childText := ""
					if s.Text() != "" {
						childText += s.Text()
					}

					for _, node := range s.Nodes {
						if node.Type == html.TextNode {
							childText += node.Data
						}
					}
					cells = append(cells, childText)
				}
			})

			rows = append(rows, cells)
		})
		tables = append(tables, rows)
	})

	report.Tables = tables

	doc.Find("P").Each(func(i int, p *goquery.Selection) {
		if trimmed := strings.TrimSpace(p.Text()); trimmed != "" {
			report.KeyParagraphs = append(report.KeyParagraphs, trimmed)
		}
	})

	return report, nil
}

func ReportToMarkdown(report *UsefulReport) string {
	var builder strings.Builder
	// --- Convert Metadata ---
	builder.WriteString(fmt.Sprintf("# %s\n\n", report.ReportTitle))
	builder.WriteString(fmt.Sprintf("**Company:** %s\n", report.CompanyName))
	builder.WriteString(fmt.Sprintf("**CIK:** %s\n\n", report.CompanyCIK))
	builder.WriteString("---\n\n") // Horizontal rule

	// --- Convert Tables ---
	for i, table := range report.Tables {
		if len(table) == 0 {
			continue // Skip empty tables
		}

		builder.WriteString(fmt.Sprintf("## Table %d\n\n", i+1))

		// Assume the first row is the header
		headers := table[0]
		numCols := len(headers)

		// Write Header
		builder.WriteString("|")
		for _, header := range headers {
			// Clean up cell content for Markdown
			cell := strings.TrimSpace(strings.ReplaceAll(header, "\n", " "))
			builder.WriteString(fmt.Sprintf(" %s |", cell))
		}
		builder.WriteString("\n")

		// Write Separator
		builder.WriteString("|")
		for j := 0; j < numCols; j++ {
			builder.WriteString(" --- |")
		}
		builder.WriteString("\n")

		// Write Data Rows
		for _, row := range table[1:] {
			builder.WriteString("|")
			for j := 0; j < numCols; j++ {
				var cell string
				if j < len(row) {
					cell = row[j]
				}
				// Clean up cell content
				cell = strings.TrimSpace(strings.ReplaceAll(cell, "\n", " "))
				builder.WriteString(fmt.Sprintf(" %s |", cell))
			}
			builder.WriteString("\n")
		}
		builder.WriteString("\n---\n\n") // Separator between tables
	}

	// --- Convert Key Paragraphs ---
	if len(report.KeyParagraphs) > 0 {
		builder.WriteString("## Key Paragraphs\n\n")
		for _, p := range report.KeyParagraphs {
			// Format as blockquote
			builder.WriteString(fmt.Sprintf("> %s\n", p))
		}
	}

	return builder.String()
}
