/**
 * API Client for P1 Strategy Builder
 */

// P1: Frontend 3000 → Backend 8000 (via Next.js rewrites proxy)
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  message?: string;
  logs?: LogEntry[];
}

export interface LogEntry {
  type: "info" | "success" | "error" | "warning";
  message: string;
  timestamp: string;
}

class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new ApiError(response.status, errorText);
  }
  return response.json();
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse<T>(response);
}

export async function apiPost<T>(
  path: string,
  body?: unknown
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(response);
}

export async function apiPut<T>(
  path: string,
  body?: unknown
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(response);
}

export async function apiDelete<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse<T>(response);
}

/**
 * WebSocket base URL 반환.
 * - NEXT_PUBLIC_API_URL 설정 시: http→ws 변환 (dev/prod 자동 대응)
 * - 미설정 시: 동일 origin 사용 (프로덕션 same-origin 배포)
 *
 * ⚠️ 로컬 개발 시 .env.local에 반드시 설정:
 *    NEXT_PUBLIC_API_URL=http://localhost:8000
 */
export function getWsBase(): string {
  if (API_BASE) return API_BASE.replace(/^http/, "ws");
  if (typeof window === "undefined") return "ws://localhost:8000";
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}`;
}

export { ApiError, API_BASE };
