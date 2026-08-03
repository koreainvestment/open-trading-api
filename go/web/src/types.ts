// Types migrated from legacy code
export interface Company {
  ID?: number;
  CorpCode?: string;
  CorpName?: string;
  CorpEngName?: string;
  LastModifiedDate?: string;
  CreatedAt?: string;
  UpdatedAt?: string;
  // Fallback fields
  id?: number;
  corp_code?: string;
  corp_name?: string;
  corp_name_eng?: string;
  name?: string;
}

export interface RawReport {
  ID?: number;
  ReceiptNumber?: string;
  CorpCode?: string;
  BlobData?: string | Uint8Array;
  BlobSize?: number;
  JSONData?: string | Record<string, unknown>;
  CreatedAt?: string;
  UpdatedAt?: string;
  // Fallback fields
  id?: number;
  receipt_number?: string;
  receiptNumber?: string;
  recept_no?: string;
  corp_code?: string;
  corpCode?: string;
  blob_data?: string | Uint8Array;
  blob_size?: number;
  json_data?: string | Record<string, unknown>;
  createdAt?: string;
  updatedAt?: string;
  date?: string;
  recept_dt?: string;
  report_nm?: string;
  reportName?: string;
}

export interface RawReportResponse {
  raw_report: string;
}

export interface CompaniesResponse {
  companies: Company[];
}

export interface ReportsResponse {
  reports: RawReport[];
}

export interface HealthResponse {
  status: string;
}

export type AnalysisRecord = RawReport & {
  RawReportID?: number;
  Analysis?: unknown;
  created_at?: string;
  [key: string]: unknown;
};

// Helper to get field value with multiple possible keys
export function getFieldValue<T>(
  obj: Record<string, unknown>,
  ...keys: string[]
): T | undefined {
  for (const key of keys) {
    const value = obj[key];
    if (value !== undefined && value !== null) {
      return value as T;
    }
  }
  return undefined;
}
