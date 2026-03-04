/**
 * Hook for managing localStorage strategies
 */

import { useState, useEffect, useCallback } from "react";
import type { StoredStrategy, BuilderState } from "@/types/builder";
import {
  loadAllStrategies,
  saveStrategy,
  deleteStrategy,
  duplicateStrategy,
  isStorageAvailable,
  getStorageInfo,
} from "@/lib/builder/storage";

export function useLocalStrategies() {
  const [strategies, setStrategies] = useState<StoredStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [storageAvailable, setStorageAvailable] = useState(false);

  // Load strategies on mount
  useEffect(() => {
    setStorageAvailable(isStorageAvailable());
    setStrategies(loadAllStrategies());
    setIsLoading(false);
  }, []);

  // Refresh strategies
  const refresh = useCallback(() => {
    setStrategies(loadAllStrategies());
  }, []);

  // Save strategy
  const save = useCallback(
    (state: BuilderState, existingId?: string): StoredStrategy => {
      const saved = saveStrategy(state, existingId);
      refresh();
      return saved;
    },
    [refresh]
  );

  // Delete strategy
  const remove = useCallback(
    (id: string): boolean => {
      const success = deleteStrategy(id);
      if (success) {
        refresh();
      }
      return success;
    },
    [refresh]
  );

  // Duplicate strategy
  const duplicate = useCallback(
    (id: string): StoredStrategy | null => {
      const duplicated = duplicateStrategy(id);
      if (duplicated) {
        refresh();
      }
      return duplicated;
    },
    [refresh]
  );

  // Get storage info
  const storageInfo = useCallback(() => {
    return getStorageInfo();
  }, []);

  return {
    strategies,
    isLoading,
    storageAvailable,
    save,
    remove,
    duplicate,
    refresh,
    storageInfo,
  };
}

export type UseLocalStrategiesReturn = ReturnType<typeof useLocalStrategies>;
