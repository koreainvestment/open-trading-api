import { useState, useEffect } from "react";
import { getFieldValue } from "../types";
import type { Company, AnalysisRecord } from "../types";
import { apiRequest } from "../api";
import { CompanySelect } from "../components/CompanySelect";
import { ReportDetail } from "../components/ReportDetail";

export function Dashboard() {
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [reports, setReports] = useState<AnalysisRecord[]>([]);
  const [selectedReportId, setSelectedReportId] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<string>("");
  const [loading, setLoading] = useState(false);

  // Fetch reports when company changes
  useEffect(() => {
    if (!selectedCompany) {
      setReports([]);
      return;
    }
    const code = getFieldValue<string>(
      selectedCompany as unknown as Record<string, unknown>,
      "corp_code"
    );
    if (!code) return;

    const fetchReports = async () => {
      setLoading(true);
      try {
        const data = await apiRequest<
          { reports: AnalysisRecord[] } | AnalysisRecord[]
        >(`/reports/${code}?limit=100`);
        setReports(Array.isArray(data) ? data : data.reports || []);
      } catch (e) {
        console.error(e);
        setReports([]);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, [selectedCompany]);

  // Derived state: Filtered Reports
  const filteredReports = reports.filter((r) => {
    if (!selectedYear) return true;
    const d = getFieldValue<string>(
      r as unknown as Record<string, unknown>,
      "created_at"
    );
    return d && new Date(d).getFullYear().toString() === selectedYear;
  });

  const activeReport = filteredReports.find(
    (r) =>
      String(
        getFieldValue(
          r as unknown as Record<string, unknown>,
          "RawReportID",
          "raw_report_id"
        )
      ) === selectedReportId
  );

  return (
    <div className="tab-content active">
      <div className="filters">
        <div className="filter-group">
          <label>Company:</label>
          <CompanySelect
            selectedCompany={selectedCompany}
            onSelect={(c) => {
              setSelectedCompany(c);
              setSelectedReportId("");
              setSelectedYear("");
            }}
          />
        </div>
        <div className="filter-group">
          <label>Report:</label>
          <select
            disabled={!selectedCompany}
            value={selectedReportId}
            onChange={(e) => setSelectedReportId(e.target.value)}
          >
            <option value="">Select a report</option>
            {filteredReports.map((r) => {
              const id = getFieldValue<string | number>(
                r as unknown as Record<string, unknown>,
                "RawReportID",
                "raw_report_id"
              );
              const date = getFieldValue<string>(
                r as unknown as Record<string, unknown>,
                "CreatedAt",
                "created_at"
              );
              return (
                <option key={String(id)} value={String(id)}>
                  Report {id}{" "}
                  {date ? ` - ${new Date(date).toLocaleDateString()}` : ""}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      <div className="content">
        {loading && (
          <div className="loading">
            <div className="spinner"></div>Loading...
          </div>
        )}

        {!loading && activeReport && (
          <div className="results">
            <ReportDetail
              report={activeReport}
              corpCode={getFieldValue(
                selectedCompany! as unknown as Record<string, unknown>,
                "corp_code"
              )}
            />
          </div>
        )}
      </div>
    </div>
  );
}
