import { useState, useEffect, Fragment } from "react";
import { getFieldValue } from "../types";
import type { Company, AnalysisRecord } from "../types";
import { apiRequest } from "../api";
import { CompanySelect } from "../components/CompanySelect";
import { ReportDetail } from "../components/ReportDetail";

export function ReportsList() {
  const [reports, setReports] = useState<AnalysisRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // Filters
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // Expanded Row State (keyed by receipt_number / rowKey)
  const [expandedRowKey, setExpandedRowKey] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const controller = new AbortController();

    const fetchAll = async () => {
      setLoading(true);
      try {
        let endpoint = "/reports?limit=100";
        if (selectedCompany) {
          const code = getFieldValue<string>(
            selectedCompany as unknown as Record<string, unknown>,
            "corp_code"
          );
          if (code) {
            endpoint += `&corp_code=${code}`;
          }
        }

        if (startDate) {
          endpoint += `&start_date=${startDate}`;
        }

        if (endDate) {
          endpoint += `&end_date=${endDate}`;
        }

        const data = await apiRequest<
          { reports: AnalysisRecord[] } | AnalysisRecord[]
        >(endpoint, { signal: controller.signal });
        if (!active) return;
        setReports(Array.isArray(data) ? data : data.reports || []);
      } catch (e) {
        if (!active) return;
        console.error(e);
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchAll();
    setExpandedRowKey(null);

    return () => {
      active = false;
      controller.abort();
    };
  }, [selectedCompany, startDate, endDate]);

  const toggleRow = (key: string) => {
    setExpandedRowKey(expandedRowKey === key ? null : key);
  };

  return (
    <div className="tab-content active">
      <div className="filters">
        <div className="filter-group">
          <label>Company:</label>
          <CompanySelect
            selectedCompany={selectedCompany}
            onSelect={setSelectedCompany}
            placeholder="Search company (optional)..."
          />
        </div>
        <div className="filter-group">
          <label>Start Date:</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <label>End Date:</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>

      <div className="results">
        {loading ? (
          <div className="loading">
            <div className="spinner"></div>Loading...
          </div>
        ) : reports.length === 0 ? (
          <div className="empty-state">No matching reports</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Corp Code</th>
                <th>Corp Name</th>
                <th>Name</th>
                <th>Date</th>
                <th>Receipt #</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => {
                const row = r as unknown as Record<string, unknown>;
                const rowKey = String(
                  getFieldValue<string | number>(
                    row,
                    "receipt_number",
                    "raw_report_id"
                  ) ?? ""
                );
                const code = getFieldValue<string>(row, "corp_code") || "-";
                const corpName = getFieldValue<string>(row, "corp_name") || "-";
                const name = getFieldValue<string>(row, "report_name") || "-";
                const date = getFieldValue<string>(row, "receipt_date");
                const receipt =
                  getFieldValue<string>(row, "receipt_number") ||
                  getFieldValue<string | number>(row, "raw_report_id") ||
                  "-";

                return (
                  <Fragment key={rowKey}>
                    <tr
                      onClick={() => toggleRow(rowKey)}
                      style={{
                        cursor: "pointer",
                        background:
                          expandedRowKey === rowKey ? "#f1f5f9" : "inherit",
                      }}
                    >
                      <td>{code}</td>
                      <td>{corpName}</td>
                      <td>{name}</td>
                      <td>{date}</td>
                      <td>{receipt}</td>
                    </tr>
                    {expandedRowKey === rowKey && (
                      <tr className="detail-row">
                        <td colSpan={5}>
                          <div className="detail-content">
                            <ReportDetail report={r} />
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

