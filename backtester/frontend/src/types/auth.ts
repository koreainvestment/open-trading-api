/**
 * Authentication Types
 */

export type AuthMode = "vps" | "prod";

export interface AuthStatus {
  authenticated: boolean;
  mode: AuthMode;
  mode_display?: string;
  account?: string;
  can_switch_mode?: boolean;
  cooldown_remaining?: number;
}

export interface LoginRequest {
  mode: AuthMode;
}

export interface LoginResponse {
  status: "success" | "error";
  authenticated: boolean;
  mode: AuthMode;
  mode_display?: string;
  can_switch_mode?: boolean;
  cooldown_remaining?: number;
}

export interface SwitchModeRequest {
  mode: AuthMode;
}

export interface SwitchModeResponse {
  status: "success" | "error";
  message?: string;
  authenticated: boolean;
  mode: AuthMode;
  mode_display?: string;
  can_switch_mode?: boolean;
  cooldown_remaining?: number;
}
