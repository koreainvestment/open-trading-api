package xbrl

import (
	"bytes"
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"regexp"
	"strings"
)

type DocumentWrapper struct {
	XMLName      xml.Name `xml:"DOCUMENT"`
	DocumentName string   `xml:"DOCUMENT-NAME"`
	CompanyName  string   `xml:"COMPANY-NAME"`
	Body         Body     `xml:"BODY"`
}

type Body struct {
	Section1 Section1 `xml:"SECTION-1"`
}

type Section1 struct {
	Title   string   `xml:"TITLE"`
	PSL     []string `xml:"P"`       // paragraphs
	Tables  []Table  `xml:"TABLE"`   // you can define Table struct
	Library Library  `xml:"LIBRARY"` // nested library info
}

type Table struct {
	TBODY TBODY `xml:"TBODY"`
}

type TBODY struct {
	Rows []TR `xml:"TR"`
}

type TR struct {
	TDs []TD `xml:"TD"`
}

type TD struct {
	Text string `xml:",chardata"`
}

type Library struct {
	TableGroups []TableGroup `xml:"TABLE-GROUP"`
	Images      []Image      `xml:"IMAGE"`
}

type TableGroup struct {
	Tables []Table `xml:"TABLE"`
}

type Image struct {
	Img     string `xml:"IMG"`
	Caption string `xml:"IMG-CAPTION"`
}

// 2. Define XBRL instance structs (simplified)
type XbrlInstance struct {
	XMLName  xml.Name  `xml:"xbrl"`
	Contexts []Context `xml:"context"`
	Units    []Unit    `xml:"unit"`
	Facts    []Fact    `xml:",any"` // capture any fact tag
}

type Context struct {
	ID     string `xml:"id,attr"`
	Entity Entity `xml:"entity"`
	Period Period `xml:"period"`
}

type Entity struct {
	Identifier Identifier `xml:"identifier"`
}

type Identifier struct {
	Text   string `xml:",chardata"`
	Scheme string `xml:"scheme,attr"`
}

type Period struct {
	Instant   string `xml:"instant,omitempty"`
	StartDate string `xml:"startDate,omitempty"`
	EndDate   string `xml:"endDate,omitempty"`
}

type Unit struct {
	ID      string `xml:"id,attr"`
	Measure string `xml:"measure"`
}

type Fact struct {
	XMLName    xml.Name
	ContextRef string `xml:"contextRef,attr"`
	UnitRef    string `xml:"unitRef,attr,omitempty"`
	Decimals   string `xml:"decimals,attr,omitempty"`
	Value      string `xml:",chardata"`
}

type Node struct {
	Name       string            `json:"name"`
	Attributes map[string]string `json:"attributes,omitempty"`
	Text       string            `json:"text,omitempty"`
	Children   []*Node           `json:"children,omitempty"`
}

// UsefulReport is the structured output you care about
type UsefulReport struct {
	CompanyName   string       `json:"company_name,omitempty"`
	ReportTitle   string       `json:"report_title,omitempty"`
	CompanyCIK    string       `json:"company_cik,omitempty"`
	Date          string       `json:"date,omitempty"`
	Tables        [][][]string `json:"tables,omitempty"` // each table is rows of cells
	KeyParagraphs []string     `json:"key_paragraphs,omitempty"`
	Facts         []FactValue  `json:"facts,omitempty"`
}

// FactValue represents an XBRL-style fact if present
type FactValue struct {
	Concept    string `json:"concept"`
	Value      string `json:"value"`
	ContextRef string `json:"context_ref,omitempty"`
	UnitRef    string `json:"unit_ref,omitempty"`
}

var reXMLTag = regexp.MustCompile(`<\/?[^>]+>`)
var reMeta = regexp.MustCompile(`(?i)<meta\b([^>]+)>`)
var reBr = regexp.MustCompile(`(?i)<br\b([^>]+)>`)

var xmlTagNames = []string{"COMPANY-NAME", "TABLE", "SECTION-2", "COVER-TITLE", "TD", "IMG-CAPTION", "TR", "TU", "TITLE", "THEAD", "LIBRARY", "DOCUMENT-NAME", "SECTION-3", "SUMMARY", "EXTRACTION", "BODY", "COLGROUP", "COL", "IMAGE", "DOCUMENT", "COVER", "TBODY", "IMG", "P", "TABLE-GROUP", "PGBRK", "TE", "SPAN", "FORMULA-VERSION", "SECTION-1", "TH", "A", "PART", "?xml", "CORRECTION"}

// parseNode recursively builds a Node from the current xml.StartElement
func parseNode(dec *xml.Decoder, start xml.StartElement) (*Node, error) {
	node := &Node{
		Name:       start.Name.Local,
		Attributes: make(map[string]string),
	}

	for _, attr := range start.Attr {
		node.Attributes[attr.Name.Local] = attr.Value
	}

	for {
		tok, err := dec.Token()
		if err != nil {
			if err == io.EOF {
				return node, nil
			}

			return nil, err
		}
		switch t := tok.(type) {
		case xml.StartElement:
			child, err := parseNode(dec, t)
			if err != nil {
				return nil, err
			}
			node.Children = append(node.Children, child)
		case xml.CharData:
			text := string(t)
			if len(text) > 0 {
				text := string(t)
				if trimmed := strings.TrimSpace(text); trimmed != "" {
					node.Text += trimmed
				}
			}
		case xml.EndElement:
			if t.Name.Local == start.Name.Local {
				return node, nil
			}
		}
	}
}

// ConvertXMLToJSON takes raw XML bytes, parses/traverses everything, returns JSON bytes.
func ConvertXMLToJSON(xmlBytes []byte) ([]byte, error) {
	dec := xml.NewDecoder(bytes.NewReader(xmlBytes))

	// find the first StartElement (root)
	for {
		tok, err := dec.Token()
		if err != nil {
			return nil, fmt.Errorf("error reading xml token: %w", err)
		}
		if start, ok := tok.(xml.StartElement); ok {
			rootNode, err := parseNode(dec, start)
			if err != nil {
				return nil, fmt.Errorf("error parsing xml node: %w", err)
			}
			// marshal to JSON
			out, err := json.MarshalIndent(rootNode, "", "  ")
			if err != nil {
				return nil, fmt.Errorf("json marshal error: %w", err)
			}
			return out, nil
		}
	}
}

func ParseDocument(data []byte) (interface{}, error) {
	dec := xml.NewDecoder(bytes.NewReader(data))
	for {
		tok, err := dec.Token()
		if err != nil {
			return nil, fmt.Errorf("reading xml token: %w", err)
		}
		if se, ok := tok.(xml.StartElement); ok {
			switch se.Name.Local {
			case "DOCUMENT":
				var docWrap DocumentWrapper
				if err := xml.Unmarshal(data, &docWrap); err != nil {
					return nil, fmt.Errorf("unmarshal DocumentWrapper: %w", err)
				}
				return &docWrap, nil
			case "xbrl":
				var inst XbrlInstance
				if err := xml.Unmarshal(data, &inst); err != nil {
					return nil, fmt.Errorf("unmarshal XbrlInstance: %w", err)
				}
				return &inst, nil
			default:
				return nil, fmt.Errorf("unknown root element: %s", se.Name.Local)
			}
		}
	}
}

// ConvertXMLToNode builds the full tree of Nodes
func ConvertXMLToNode(xmlBytes []byte) (*Node, error) {
	dec := xml.NewDecoder(bytes.NewReader(xmlBytes))
	for {
		tok, err := dec.Token()
		if err != nil {
			return nil, fmt.Errorf("error reading xml token: %w", err)
		}
		if start, ok := tok.(xml.StartElement); ok {
			root, err := parseNode(dec, start)
			if err != nil {
				return nil, fmt.Errorf("error parsing xml tree for tag: %s: %w", start.Name.Local, err)
			}
			return root, nil
		}
	}
}

// ExtractUseful traverses the Node tree and extracts structured UsefulReport
func ExtractUseful(root *Node) UsefulReport {
	var out UsefulReport

	// Example: extract company name from node named "COMPANY-NAME"
	if n := findFirst(root, "COMPANY-NAME"); n != nil {
		out.CompanyName = n.Text
	}
	// Example: extract report title from node named "DOCUMENT-NAME"
	if n := findFirst(root, "DOCUMENT-NAME"); n != nil {
		out.ReportTitle = n.Text
	}
	// Example: simple date extraction, maybe from "RCEPT-DT" or other
	if n := findFirst(root, "RCEPT-DT"); n != nil {
		out.Date = n.Text
	}

	// Extract tables
	tableNodes := findAll(root, "TABLE")
	tags := []string{"TD", "TH", "TU", "TE"}
	for _, t := range tableNodes {
		var rows [][]string
		for _, tr := range findAll(t, "TR") {
			var cells []string
			for _, td := range findAllByTags(tr, tags) {
				childText := ""
				if td.Text != "" {
					childText += td.Text
				}

				for _, child := range td.Children {
					if child.Text != "" {
						childText += child.Text
					}
				}

				if childText != "" {
					cells = append(cells, childText)
				}

			}
			rows = append(rows, cells)
		}
		if len(rows) > 0 {
			out.Tables = append(out.Tables, rows)
		}
	}

	// Extract key paragraphs (example: all <P> nodes)
	for _, p := range findAll(root, "P") {
		if trimmed := strings.TrimSpace(p.Text); trimmed != "" {
			out.KeyParagraphs = append(out.KeyParagraphs, trimmed)
		}
	}

	// Extract facts if XBRL present: simple heuristic: nodes with attribute contextRef
	var facts []FactValue
	traverse(root, func(n *Node) {
		if val, ok := n.Attributes["contextRef"]; ok {
			fv := FactValue{
				Concept:    n.Name,
				Value:      n.Text,
				ContextRef: val,
				UnitRef:    n.Attributes["unitRef"],
			}
			facts = append(facts, fv)
		}
	})
	out.Facts = facts

	return out
}

// ConvertXMLToUsefulJSON is the top-level function you call
func ConvertXMLToUsefulJSON(xmlBytes []byte) ([]byte, error) {
	cleanedXmlString := string(xmlBytes)

	if strings.Contains(cleanedXmlString, "&") {
		cleanedXmlString = strings.ReplaceAll(cleanedXmlString, "&", "&amp;")
	}

	if strings.Contains(cleanedXmlString, "<<") {
		cleanedXmlString = strings.ReplaceAll(cleanedXmlString, "<<", "&lt;<")
	}

	if strings.Contains(cleanedXmlString, ">>") {
		cleanedXmlString = strings.ReplaceAll(cleanedXmlString, ">>", ">&gt;")
	}

	if reXMLTag.MatchString(cleanedXmlString) {
		matches := reXMLTag.FindAllStringSubmatch(cleanedXmlString, -1)
		for _, match := range matches {
			tagName := strings.TrimPrefix(match[0], "<")
			tagName = strings.TrimPrefix(tagName, "/")
			tagName = strings.Split(tagName, " ")[0]
			tagName = strings.TrimSuffix(tagName, ">")

			if !isValidTagName(tagName) {
				fmt.Printf("unmatch: %s, %s\n", match[0], tagName)
				cleanedXmlString = strings.ReplaceAll(cleanedXmlString, match[0], "")
			}
		}
	}

	if reMeta.MatchString(cleanedXmlString) {
		cleanedXmlString = reMeta.ReplaceAllString(cleanedXmlString, `<meta$1/>`)
	}

	if reBr.MatchString(cleanedXmlString) {
		cleanedXmlString = reBr.ReplaceAllString(cleanedXmlString, `<br$1/>`)
	}

	root, err := ConvertXMLToNode([]byte(cleanedXmlString))
	if err != nil {
		return nil, err
	}

	useful := ExtractUseful(root)
	b, err := json.MarshalIndent(useful, "", "  ")
	if err != nil {
		return nil, fmt.Errorf("json marshal error: %w", err)
	}
	return b, nil
}

// Helper: traverse all nodes and apply action
func traverse(n *Node, action func(*Node)) {
	action(n)
	for _, c := range n.Children {
		traverse(c, action)
	}
}

// Helper: find first node with given name
func findFirst(n *Node, name string) *Node {
	if n.Name == name {
		return n
	}
	for _, c := range n.Children {
		if found := findFirst(c, name); found != nil {
			return found
		}
	}
	return nil
}

// Helper: find all nodes with given name
func findAll(n *Node, name string) []*Node {
	var result []*Node
	if strings.EqualFold(n.Name, name) {
		result = append(result, n)
	}
	for _, c := range n.Children {
		result = append(result, findAll(c, name)...)
	}
	return result
}

func findAllByTags(n *Node, tags []string) []*Node {
	var result []*Node
	for _, tag := range tags {
		result = append(result, findAll(n, tag)...)
	}
	return result
}

func isValidTagName(tagName string) bool {
	for _, tag := range xmlTagNames {
		if strings.EqualFold(tag, tagName) {
			return true
		}
	}
	return false
}
