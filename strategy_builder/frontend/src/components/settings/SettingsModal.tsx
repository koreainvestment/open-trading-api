"use client";

import { useState, useEffect } from "react";
import { X, RefreshCw, Database, Shield, Clock } from "lucide-react";
import { useAuth } from "@/hooks";
import { getMasterStatus, collectMasterFiles } from "@/lib/api/symbols";
import type { MasterStatus } from "@/types/symbols";
import type { AuthMode } from "@/types/auth";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { status, isLoading, error, login, switchMode } = useAuth();
  const [masterStatus, setMasterStatus] = useState<MasterStatus | null>(null);
  const [isCollecting, setIsCollecting] = useState(false);
  const [cooldownTimer, setCooldownTimer] = useState(0);

  // Fetch master status on mount
  useEffect(() => {
    if (isOpen) {
      fetchMasterStatus();
    }
  }, [isOpen]);

  // Cooldown timer - 실시간으로 감소
  useEffect(() => {
    if (status.cooldown_remaining && status.cooldown_remaining > 0) {
      setCooldownTimer(status.cooldown_remaining);
    }
  }, [status.cooldown_remaining]);

  useEffect(() => {
    if (cooldownTimer > 0) {
      const interval = setInterval(() => {
        setCooldownTimer((prev) => Math.max(0, prev - 1));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [cooldownTimer]);

  const fetchMasterStatus = async () => {
    try {
      const result = await getMasterStatus();
      setMasterStatus(result);
    } catch (error) {
      console.error("Failed to fetch master status:", error);
    }
  };

  const handleCollectMaster = async () => {
    setIsCollecting(true);
    try {
      const result = await collectMasterFiles();
      await fetchMasterStatus();
      if (!result.success && result.errors?.length) {
        console.error("Collection errors:", result.errors);
      }
    } catch (error) {
      console.error("Failed to collect master files:", error);
    } finally {
      setIsCollecting(false);
    }
  };

  const handleLogin = async (mode: AuthMode) => {
    await login(mode);
  };

  const handleSwitchMode = async () => {
    const newMode = status.mode === "vps" ? "prod" : "vps";
    const success = await switchMode(newMode);
    if (success) {
      setCooldownTimer(60);
    }
  };

  if (!isOpen) return null;

  const canSwitch = status.can_switch_mode !== false && cooldownTimer === 0;
  const isVps = status.mode === "vps";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-white dark:bg-slate-900 rounded-xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <h2 className="text-lg font-semibold">설정</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-6">
          {/* Authentication & Mode Section */}
          <section className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
              <Shield className="w-4 h-4" />
              인증 및 모드
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-3">
              {/* 현재 상태 표시 */}
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600 dark:text-slate-400">인증 상태</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                  status.authenticated
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                }`}>
                  {status.authenticated ? "인증됨" : "미인증"}
                </span>
              </div>
              {status.authenticated && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 dark:text-slate-400">현재 모드</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                    isVps
                      ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
                      : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                  }`}>
                    {status.mode_display || (isVps ? "모의투자" : "실전투자")}
                  </span>
                </div>
              )}

              {/* 쿨다운 표시 */}
              {cooldownTimer > 0 && (
                <div className="flex items-center gap-2 p-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                  <Clock className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                  <span className="text-sm text-amber-600 dark:text-amber-400 font-medium">
                    쿨다운: {cooldownTimer}초 남음
                  </span>
                  <div className="flex-1 h-1 bg-amber-200 dark:bg-amber-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-amber-500 transition-all duration-1000"
                      style={{ width: `${(cooldownTimer / 60) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* 모드 전환 버튼 */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => {
                    // 모의투자 버튼
                    if (!status.authenticated) {
                      handleLogin("vps");
                    } else if (!isVps && canSwitch) {
                      handleSwitchMode();
                    }
                  }}
                  disabled={isLoading || (status.authenticated && isVps) || (status.authenticated && !isVps && !canSwitch)}
                  className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                    isVps && status.authenticated
                      ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400 ring-2 ring-yellow-500 cursor-default"
                      : isLoading
                        ? "bg-slate-100 dark:bg-slate-700 opacity-50"
                        : "bg-slate-100 dark:bg-slate-700 hover:bg-yellow-50 dark:hover:bg-yellow-900/20"
                  }`}
                >
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span className="w-2 h-2 rounded-full bg-yellow-500" />
                      모의투자
                    </>
                  )}
                </button>
                <button
                  onClick={() => {
                    // 실전투자 버튼
                    if (!status.authenticated) {
                      handleLogin("prod");
                    } else if (isVps && canSwitch) {
                      handleSwitchMode();
                    }
                  }}
                  disabled={isLoading || (status.authenticated && !isVps) || (status.authenticated && isVps && !canSwitch)}
                  className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                    !isVps && status.authenticated
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 ring-2 ring-green-500 cursor-default"
                      : isLoading
                        ? "bg-slate-100 dark:bg-slate-700 opacity-50"
                        : "bg-slate-100 dark:bg-slate-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                  }`}
                >
                  {isLoading ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <>
                      <span className="w-2 h-2 rounded-full bg-green-500" />
                      실전투자
                    </>
                  )}
                </button>
              </div>

              {error && (
                <div className="px-2 py-1.5 rounded bg-red-50 dark:bg-red-900/20 text-xs text-red-600 dark:text-red-400">
                  {error}
                </div>
              )}

              <p className="text-xs text-slate-500 dark:text-slate-400 text-center">
                모드 전환은 1분에 1회만 가능합니다
              </p>
            </div>
          </section>

          {/* Master File Status */}
          <section className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
              <Database className="w-4 h-4" />
              종목 마스터파일
            </div>
            <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-3">
              {masterStatus ? (
                <>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600 dark:text-slate-400">코스피</span>
                      <span className="font-mono">{masterStatus.kospi_count.toLocaleString()}개</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-600 dark:text-slate-400">코스닥</span>
                      <span className="font-mono">{masterStatus.kosdaq_count.toLocaleString()}개</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-600 dark:text-slate-400">총 종목 수</span>
                    <span className="font-mono font-bold">{masterStatus.total_count.toLocaleString()}개</span>
                  </div>
                  {masterStatus.kospi_updated && (
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      마지막 업데이트: {new Date(masterStatus.kospi_updated).toLocaleString()}
                    </div>
                  )}
                  {masterStatus.needs_update && (
                    <div className="text-xs text-amber-600 dark:text-amber-400">
                      업데이트가 필요합니다
                    </div>
                  )}
                </>
              ) : (
                <div className="text-sm text-slate-500 dark:text-slate-400">
                  로딩 중...
                </div>
              )}
              <button
                onClick={handleCollectMaster}
                disabled={isCollecting}
                className="w-full py-2 px-4 rounded-lg text-sm font-medium bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 transition-colors"
              >
                {isCollecting ? (
                  <span className="flex items-center justify-center gap-2">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    수집 중...
                  </span>
                ) : (
                  "마스터파일 수집"
                )}
              </button>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}

export default SettingsModal;
