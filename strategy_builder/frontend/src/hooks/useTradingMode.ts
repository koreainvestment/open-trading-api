"use client";

import { useState, useEffect } from "react";
import { useAuth } from "./useAuth";
import type { AuthMode } from "@/types/auth";

interface UseTradingModeReturn {
  mode: AuthMode;
  modeDisplay: string;
  isVps: boolean;
  isProd: boolean;
  isLoading: boolean;
  canSwitch: boolean;
  cooldownRemaining: number;
  switchToVps: () => Promise<boolean>;
  switchToProd: () => Promise<boolean>;
  toggle: () => Promise<boolean>;
}

/**
 * useTradingMode hook - 트레이딩 모드 관리
 * 
 * 모의투자(vps) / 실전투자(prod) 모드 전환을 관리합니다.
 * 1분 쿨다운이 적용됩니다.
 */
export function useTradingMode(): UseTradingModeReturn {
  const { status, isLoading, switchMode } = useAuth();
  const [cooldownTimer, setCooldownTimer] = useState(0);

  // Cooldown timer countdown
  useEffect(() => {
    if (status.cooldown_remaining && status.cooldown_remaining > 0) {
      setCooldownTimer(status.cooldown_remaining);
    }
  }, [status.cooldown_remaining]);

  useEffect(() => {
    if (cooldownTimer <= 0) return;

    const interval = setInterval(() => {
      setCooldownTimer((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(interval);
  }, [cooldownTimer]);

  const mode = status.mode;
  const isVps = mode === "vps";
  const isProd = mode === "prod";
  const canSwitch = status.authenticated && (status.can_switch_mode !== false) && cooldownTimer === 0;
  const modeDisplay = status.mode_display || (isVps ? "모의투자" : "실전투자");

  const switchToVps = async () => {
    if (!canSwitch || isVps) return false;
    const success = await switchMode("vps");
    if (success) {
      setCooldownTimer(60);
    }
    return success;
  };

  const switchToProd = async () => {
    if (!canSwitch || isProd) return false;
    const success = await switchMode("prod");
    if (success) {
      setCooldownTimer(60);
    }
    return success;
  };

  const toggle = async () => {
    if (!canSwitch) return false;
    return isVps ? switchToProd() : switchToVps();
  };

  return {
    mode,
    modeDisplay,
    isVps,
    isProd,
    isLoading,
    canSwitch,
    cooldownRemaining: cooldownTimer,
    switchToVps,
    switchToProd,
    toggle,
  };
}

export default useTradingMode;
