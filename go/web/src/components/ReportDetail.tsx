import { useState } from 'react';
import { getFieldValue } from '../types';
import type { AnalysisRecord } from '../types';
import { RawReportViewer } from './RawReportViewer';

interface ReportDetailProps {
  report: AnalysisRecord;
  corpCode?: string; // Optional context, mostly needed if report doesn't have it
}

export function ReportDetail({ report, corpCode }: ReportDetailProps) {
  const [showRaw, setShowRaw] = useState(false);

  const rawReportId = getFieldValue<string | number>(report as unknown as Record<string, unknown>, "RawReportID", "raw_report_id");
  const createdAt = getFieldValue<string>(report as unknown as Record<string, unknown>, "CreatedAt", "created_at");
  const analysisData = getFieldValue<unknown>(report as unknown as Record<string, unknown>, "Analysis", "analysis");
  
  // Resolve corpCode: explicit prop > report field
  const code = corpCode || getFieldValue<string>(report as unknown as Record<string, unknown>, "CorpCode", "corp_code");

  let parsedAnalysis: unknown = analysisData;
  if (typeof analysisData === 'string') {
      try { parsedAnalysis = JSON.parse(analysisData); } catch {}
  }

  return (
    <div className="report-card">
      <h3>Report Details</h3>
      <div className="meta">
        {rawReportId && <span><strong>ID:</strong> {rawReportId}</span>}
        {createdAt && <span><strong>Date:</strong> {new Date(createdAt).toLocaleDateString()}</span>}
      </div>

      {parsedAnalysis ? (
        <div className="json-viewer">
           <h4>Analysis</h4>
           <pre>{JSON.stringify(parsedAnalysis, null, 2)}</pre>
        </div>
      ) : (
        <div className="empty-state">No analysis available</div>
      )}

      <div className="action-area">
        {!showRaw ? (
             <button className="primary-button" onClick={() => setShowRaw(true)}>Load Raw Report</button>
        ) : (
            code && rawReportId ? (
                <RawReportViewer corpCode={code} reportId={rawReportId} />
            ) : (
                <div className="error">Missing info to load raw report</div>
            )
        )}
      </div>
    </div>
  );
}
