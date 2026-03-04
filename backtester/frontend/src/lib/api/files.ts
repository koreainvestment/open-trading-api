/**
 * 파일 Import/Export API
 */

import { apiGet, apiGetBlob, apiPostForm, apiPostBlob } from "./client";
import type {
  TemplateListResponse,
  TemplateDetailResponse,
  ImportResult,
  ValidationResult,
} from "@/types";

/**
 * 템플릿 목록 조회
 */
export async function listTemplates(): Promise<TemplateListResponse> {
  return apiGet("/api/files/templates");
}

/**
 * 템플릿 상세 조회 (YAML 포함)
 */
export async function getTemplate(id: string): Promise<TemplateDetailResponse> {
  return apiGet(`/api/files/templates/${encodeURIComponent(id)}`);
}

/**
 * 템플릿 Python 코드 조회
 */
export async function getTemplatePython(id: string): Promise<{
  success: boolean;
  data: { id: string; name: string; python: string };
}> {
  return apiGet(`/api/files/templates/${encodeURIComponent(id)}/python`);
}

/**
 * 템플릿 다운로드
 */
export async function downloadTemplate(id: string): Promise<Blob> {
  return apiGetBlob(`/api/files/templates/${encodeURIComponent(id)}/download`);
}

/**
 * 전략 Import (YAML 파일 업로드)
 */
export async function importStrategy(file: File): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiPostForm("/api/files/import", formData);
}

/**
 * 전략 Export (YAML, Python, ZIP 파일 다운로드)
 */
export async function exportStrategy(
  strategyId: string,
  format: "yaml" | "python" | "zip" = "yaml"
): Promise<Blob> {
  return apiPostBlob(`/api/files/export/${encodeURIComponent(strategyId)}?format=${format}`);
}

/**
 * 전략 파일 검증
 */
export async function validateFile(file: File): Promise<ValidationResult> {
  const formData = new FormData();
  formData.append("file", file);
  return apiPostForm("/api/files/validate", formData);
}

/**
 * 파일 다운로드 헬퍼
 */
export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
