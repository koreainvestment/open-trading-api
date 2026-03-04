"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TrendingUp, Sparkles, Play, Settings } from "lucide-react";
import { useAuth } from "@/hooks";
import { SettingsModal } from "@/components/settings";

const navItems = [
  { href: "/builder", label: "전략 빌더", icon: Sparkles },
  { href: "/execute", label: "전략 실행", icon: Play },
];

export function Navigation() {
  const pathname = usePathname();
  const { status } = useAuth();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const isVps = status.mode === "vps";
  const modeLabel = isVps ? "모의" : "실전";
  const modeColor = isVps
    ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
    : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";

  return (
    <>
      <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <div className="w-full px-4">
          <div className="flex items-center justify-between h-16">
            {/* 로고 */}
            <Link href="/" className="flex items-center gap-3 focus-ring rounded-lg" aria-label="KIS Strategy Builder 홈">
              <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" aria-hidden="true" />
              </div>
              <div className="hidden sm:block">
                <h1 className="font-bold text-lg text-slate-900 dark:text-slate-100">
                  KIS Strategy Builder
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  비주얼 전략 빌더
                </p>
              </div>
            </Link>

            {/* 네비게이션 */}
            <nav className="flex items-center gap-1" aria-label="메인 네비게이션">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    aria-current={isActive ? "page" : undefined}
                    aria-label={item.label}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors focus-ring ${
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
                    }`}
                  >
                    <Icon className="w-4 h-4" aria-hidden="true" />
                    <span className="hidden sm:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            {/* 우측 영역: 모드 표시 + 설정 톱니바퀴 */}
            <div className="flex items-center gap-2">
              {/* 현재 모드 배지 - 인증된 경우에만 표시 */}
              {status.authenticated && (
                <span
                  className={`px-2 py-1 rounded text-xs font-bold ${modeColor}`}
                  role="status"
                  aria-label={`현재 모드: ${modeLabel}투자`}
                >
                  {modeLabel}
                </span>
              )}

              {/* 설정 버튼 (톱니바퀴) */}
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus-ring"
                aria-label="설정 열기"
              >
                <Settings className="w-5 h-5 text-slate-600 dark:text-slate-400" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 설정 모달 */}
      <SettingsModal 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
      />
    </>
  );
}

export default Navigation;
