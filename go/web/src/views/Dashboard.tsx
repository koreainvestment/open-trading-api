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

    let active = true;
    const controller = new AbortController();

    const fetchReports = async () => {
      setLoading(true);
      try {
        const data = await apiRequest<
          { reports: AnalysisRecord[] } | AnalysisRecord[]
        >(`/reports/${code}?limit=100`, { signal: controller.signal });
        if (!active) return;
        setReports(Array.isArray(data) ? data : data.reports || []);
      } catch (e) {
        if (!active) return;
        console.error(e);
        setReports([]);
      } finally {
        if (active) setLoading(false);
      }
    };
    fetchReports();

    return () => {
      active = false;
      controller.abort();
    };
  }, [selectedCompany]);

  const activeReport = reports.find(
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
            {reports.map((r) => {
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
