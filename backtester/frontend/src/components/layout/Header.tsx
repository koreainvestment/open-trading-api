"use client";

import { useState } from "react";
import Link from "next/link";
import { TrendingUp, Settings } from "lucide-react";
import { SettingsModal } from "@/components/settings";
import { useAuth } from "@/hooks";

export function Header() {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { status } = useAuth();

  const badgeLabel = !status.authenticated
    ? "미인증"
    : status.mode === "vps"
      ? "모의"
      : "실전";

  const badgeColor = !status.authenticated
    ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
    : status.mode === "vps"
      ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
      : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";

  return (
    <>
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <div className="w-full px-4">
          <div className="flex items-center justify-between h-16">
            {/* 로고 */}
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#245bee] flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-lg text-slate-900 dark:text-slate-100">
                  KIS Backtest
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  퀀트 전략 백테스터
                </p>
              </div>
            </Link>

            {/* 우측: 인증 배지 + 설정 버튼 */}
            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-1 rounded text-xs font-bold ${badgeColor}`}
                role="status"
                aria-label={`인증 상태: ${badgeLabel}`}
              >
                {badgeLabel}
              </span>
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                aria-label="설정 열기"
              >
                <Settings className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </>
  );
}

export default Header;
