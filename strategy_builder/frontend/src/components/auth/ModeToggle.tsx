"use client";

import { RefreshCw, Clock } from "lucide-react";
import { useAuth } from "@/hooks";

interface ModeToggleProps {
  compact?: boolean;
  className?: string;
}

export function ModeToggle({ compact = false, className = "" }: ModeToggleProps) {
  const { status, isLoading, switchMode } = useAuth();

  if (!status.authenticated) {
    return null;
  }

  const isVps = status.mode === "vps";
  const canSwitch = status.can_switch_mode !== false && (status.cooldown_remaining ?? 0) === 0;

  const handleToggle = async () => {
    if (!canSwitch) return;
    const newMode = isVps ? "prod" : "vps";
    await switchMode(newMode);
  };

  const modeColor = isVps
    ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400"
    : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400";

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className={`px-2 py-0.5 rounded text-xs font-bold ${modeColor}`}>
        {status.mode_display || (isVps ? "모의" : "실전")}
      </span>
      
      {!compact && (
        <button
          onClick={handleToggle}
          disabled={isLoading || !canSwitch}
          className={`flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors ${
            canSwitch
              ? "hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400"
              : "text-slate-400 dark:text-slate-500 cursor-not-allowed"
          }`}
          title={
            !canSwitch && status.cooldown_remaining
              ? `${status.cooldown_remaining}초 후 전환 가능`
              : undefined
          }
        >
          {isLoading ? (
            <RefreshCw className="w-3 h-3 animate-spin" />
          ) : !canSwitch && status.cooldown_remaining ? (
            <>
              <Clock className="w-3 h-3" />
              {status.cooldown_remaining}초
            </>
          ) : (
            <>
              <RefreshCw className="w-3 h-3" />
              전환
            </>
          )}
        </button>
      )}
    </div>
  );
}

export default ModeToggle;
