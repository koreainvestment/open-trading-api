"use client";

import { useState } from "react";
import { User, LogIn, LogOut, RefreshCw } from "lucide-react";
import { useAuth, useAccount } from "@/hooks";
import type { AuthMode } from "@/types/auth";

interface AuthStatusProps {
  compact?: boolean;
}

export function AuthStatus({ compact = false }: AuthStatusProps) {
  const { status, isLoading, error, login, logout, switchMode } = useAuth();
  const { info, fetchInfo } = useAccount();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogin = async (mode: AuthMode) => {
    const success = await login(mode);
    if (success) {
      await fetchInfo();
    }
    setShowDropdown(false);
  };

  const handleLogout = () => {
    logout();
    setShowDropdown(false);
  };

  const handleSwitchMode = async () => {
    const newMode = status.mode === "vps" ? "prod" : "vps";
    const success = await switchMode(newMode);
    if (success) {
      await fetchInfo();
    }
    setShowDropdown(false);
  };

  if (!status.authenticated) {
    return (
      <div className="relative">
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        >
          {isLoading ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <LogIn className="w-4 h-4" />
          )}
          {!compact && <span className="text-sm font-medium">로그인</span>}
        </button>

        {showDropdown && (
          <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 z-50">
            <div className="p-2">
              <button
                onClick={() => handleLogin("vps")}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <span className="w-2 h-2 rounded-full bg-yellow-500" />
                모의투자로 로그인
              </button>
              <button
                onClick={() => handleLogin("prod")}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <span className="w-2 h-2 rounded-full bg-green-500" />
                실전투자로 로그인
              </button>
            </div>
          </div>
        )}

        {error && (
          <p className="absolute right-0 top-full mt-1 text-xs text-red-500">{error}</p>
        )}
      </div>
    );
  }

  const isVps = status.mode === "vps" || info?.is_vps;
  const modeLabel = isVps ? "모의" : "실전";
  const modeColor = isVps
    ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
    : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
      >
        <span className={`px-2 py-0.5 rounded text-xs font-bold ${modeColor}`}>
          {modeLabel}
        </span>
        {!compact && (
          <>
            <User className="w-4 h-4 text-slate-600 dark:text-slate-400" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              {info?.account_no || "계좌"}
            </span>
          </>
        )}
      </button>

      {showDropdown && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 z-50">
          <div className="p-3 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-500">계좌번호</span>
              <span className={`px-2 py-0.5 rounded text-xs font-bold ${modeColor}`}>
                {modeLabel}
              </span>
            </div>
            <p className="mt-1 font-mono text-sm font-medium">
              {info?.account_no_full || "로딩 중..."}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              {info?.account_type || ""} 계좌
            </p>
          </div>

          <div className="p-2">
            <button
              onClick={handleSwitchMode}
              disabled={isLoading}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-md hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
              {isVps ? "실전투자로 전환" : "모의투자로 전환"}
            </button>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20"
            >
              <LogOut className="w-4 h-4" />
              로그아웃
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AuthStatus;
