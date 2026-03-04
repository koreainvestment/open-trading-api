/**
 * API 클라이언트 공통 설정
 */

// P2: Frontend 3001 → Backend 8002 (via Next.js rewrites proxy)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  message?: string;
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

export async function apiPostForm<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }
  return res.json();
}

export async function apiGetBlob(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`Download Error: ${res.status}`);
  }
  return res.blob();
}

export async function apiPostBlob(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error(`Download Error: ${res.status}`);
  }
  return res.blob();
}

export { API_BASE };
