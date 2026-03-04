/**
 * Authentication API
 *
 * Mode Switching Feature:
 * - POST /login: 인증 (모드 지정)
 * - GET /status: 인증 상태 및 모드 정보
 * - POST /switch-mode: 모드 전환 (1분 쿨다운)
 * - POST /logout: 로그아웃
 */

import { apiGet, apiPost, type ApiResponse } from "./client";
import type {
  AuthStatus,
  AuthMode,
  LoginRequest,
  LoginResponse,
  SwitchModeResponse,
} from "@/types/auth";

export async function login(mode: AuthMode = "vps"): Promise<LoginResponse> {
  const request: LoginRequest = { mode };
  return apiPost<LoginResponse>("/api/auth/login", request);
}

export async function getAuthStatus(): Promise<ApiResponse<AuthStatus>> {
  const response = await apiGet<AuthStatus>("/api/auth/status");
  return {
    status: response.authenticated ? "success" : "error",
    data: {
      authenticated: response.authenticated,
      mode: response.mode || "vps",
      mode_display: response.mode_display,
      can_switch_mode: response.can_switch_mode,
      cooldown_remaining: response.cooldown_remaining,
    },
  };
}

export async function switchMode(
  mode: AuthMode
): Promise<SwitchModeResponse> {
  return apiPost<SwitchModeResponse>("/api/auth/switch-mode", { mode });
}

export async function logout(): Promise<{ status: string; message: string }> {
  return apiPost<{ status: string; message: string }>("/api/auth/logout");
}
