"use client";

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react";
import { login as apiLogin, getAuthStatus, switchMode as apiSwitchMode, logout as apiLogout } from "@/lib/api";
import type { AuthStatus, AuthMode } from "@/types/auth";

interface AuthContextValue {
  status: AuthStatus;
  isLoading: boolean;
  error: string | null;
  login: (mode: AuthMode) => Promise<boolean>;
  logout: () => Promise<void>;
  switchMode: (mode: AuthMode) => Promise<boolean>;
  checkStatus: () => Promise<void>;
}

const DEFAULT_STATUS: AuthStatus = {
  authenticated: false,
  mode: "vps",
  can_switch_mode: true,
  cooldown_remaining: 0,
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(DEFAULT_STATUS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkStatus = useCallback(async () => {
    try {
      const response = await getAuthStatus();
      if (response.data) {
        setStatus(response.data);
      }
    } catch {
      setStatus(DEFAULT_STATUS);
    }
  }, []);

  const login = useCallback(async (mode: AuthMode): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiLogin(mode);
      
      if (response.status === "success" && response.authenticated) {
        setStatus({
          authenticated: true,
          mode: response.mode,
          mode_display: response.mode_display,
          can_switch_mode: response.can_switch_mode,
          cooldown_remaining: response.cooldown_remaining,
        });
        return true;
      } else {
        setError("인증 실패");
        return false;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "인증 오류";
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      // Ignore logout errors
    }
    setStatus(DEFAULT_STATUS);
    setError(null);
  }, []);

  const switchMode = useCallback(async (mode: AuthMode): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiSwitchMode(mode);
      
      if (response.status === "success") {
        setStatus({
          authenticated: response.authenticated,
          mode: response.mode,
          mode_display: response.mode_display,
          can_switch_mode: response.can_switch_mode,
          cooldown_remaining: response.cooldown_remaining,
        });
        return true;
      } else {
        setError(response.message || "모드 전환 실패");
        return false;
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "모드 전환 오류";
      setError(message);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check status on mount, then poll every 30s (skip when tab is hidden)
  useEffect(() => {
    checkStatus();
    const interval = setInterval(() => {
      if (document.visibilityState === "visible") {
        checkStatus();
      }
    }, 30_000);
    return () => clearInterval(interval);
  }, [checkStatus]);

  return (
    <AuthContext.Provider
      value={{
        status,
        isLoading,
        error,
        login,
        logout,
        switchMode,
        checkStatus,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}

export default AuthContext;
