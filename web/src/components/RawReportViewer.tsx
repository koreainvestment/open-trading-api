import { useState, useEffect } from 'react';
import { apiRequest } from '../api';

interface RawReportViewerProps {
  corpCode: string;
  reportId: string | number;
}

export function RawReportViewer({ corpCode, reportId }: RawReportViewerProps) {
  const [content, setContent] = useState<string | null>(null);
  const [contentType, setContentType] = useState<'html' | 'xml' | 'text'>('text');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [objUrl, setObjUrl] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await apiRequest<{ raw_report: string }>(`/reports/${corpCode}/${reportId}`);
        if (!active) return;
        
        // Decoding Logic
        const binaryString = atob(data.raw_report);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }

        const decoder = new TextDecoder("utf-8", { fatal: false });
        let decoded = decoder.decode(bytes);
        
        // Simple heuristic for EUC-KR
        if (decoded.includes('charset="euc-kr"') || decoded.includes("charset='euc-kr'")) {
             try {
                 const eucDecoder = new TextDecoder("euc-kr");
                 decoded = eucDecoder.decode(bytes);
             } catch(e) {
                 console.warn("Failed to decode EUC-KR", e);
             }
        }
        
        // Normalize charset to UTF-8
        decoded = decoded.replace(/(charset\s*=\s*["']?)euc-kr(["']?)/gi, "$1utf-8$2");

        // Detect Type
        const lower = decoded.toLowerCase();
        if (lower.includes("<html") || lower.includes("<body")) {
            setContentType('html');
        } else if (lower.startsWith("<?xml") || lower.includes("<xbrl")) {
            setContentType('xml');
        } else {
            setContentType('text');
        }

        setContent(decoded);
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        if (active) setLoading(false);
      }
    };
    
    if (corpCode && reportId) load();
    return () => { active = false; };
  }, [corpCode, reportId]);

  // Create Object URL for Iframe
  useEffect(() => {
    if (content && (contentType === 'html' || contentType === 'xml')) {
        const blob = new Blob([content], { type: contentType === 'html' ? 'text/html' : 'text/xml' });
        const url = URL.createObjectURL(blob);
        setObjUrl(url);
        return () => URL.revokeObjectURL(url);
    }
    setObjUrl(null);
  }, [content, contentType]);

  if (loading) return <div>Loading raw report...</div>;
  if (error) return <div className="error-state">{error}</div>;
  if (!content) return null;

  return (
    <div className="raw-report-viewer">
      <h4>Raw Report Content ({contentType.toUpperCase()})</h4>
      {objUrl ? (
        <iframe 
            src={objUrl} 
            sandbox="allow-scripts"
            style={{ width: '100%', height: '600px', border: '1px solid #ccc', background: 'white' }}
        />
      ) : (
        <pre style={{ whiteSpace: 'pre-wrap', maxHeight: '600px', overflow: 'auto' }}>
            {content}
        </pre>
      )}
    </div>
  );
}
