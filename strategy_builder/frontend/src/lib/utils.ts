import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 고유 ID용 난수 토큰 (crypto.getRandomValues 기반, 비보안 컨텍스트(http)에서도 동작)
 */
export function randomToken(byteLength = 8): string {
  const bytes = crypto.getRandomValues(new Uint8Array(byteLength));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * 금액 포맷 (한국 원화)
 */
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("ko-KR", {
    notation: value >= 100_000_000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  }).format(value);
}

/**
 * 퍼센트 포맷
 */
export function formatPercent(value: number, showSign = true): string {
  const sign = showSign && value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

/**
 * 날짜 포맷
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}
