"use client";

import { useAuthContext } from "@/contexts";

/**
 * useAuth hook - 전역 인증 상태에 접근
 *
 * AuthProvider 내부에서 사용해야 합니다.
 * 모든 컴포넌트가 동일한 인증 상태를 공유합니다.
 */
export function useAuth() {
  return useAuthContext();
}

export default useAuth;
