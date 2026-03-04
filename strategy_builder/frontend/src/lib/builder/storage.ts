/**
 * localStorage Helper for Custom Strategies
 */

import type { StoredStrategy, BuilderState } from "@/types/builder";

const STORAGE_KEY = "kis2_custom_strategies";
const MAX_STRATEGIES = 50;

/**
 * Generate unique ID for new strategy
 */
function generateId(): string {
  return `custom_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Load all custom strategies from localStorage
 */
export function loadAllStrategies(): StoredStrategy[] {
  if (typeof window === "undefined") {
    return [];
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return [];
    }
    const strategies = JSON.parse(stored) as StoredStrategy[];
    return strategies.sort(
      (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  } catch {
    return [];
  }
}

/**
 * Get a single strategy by ID
 */
export function getStrategy(id: string): StoredStrategy | null {
  const strategies = loadAllStrategies();
  return strategies.find((s) => s.id === id) || null;
}

/**
 * Save a new strategy or update existing one
 */
export function saveStrategy(state: BuilderState, existingId?: string): StoredStrategy {
  const strategies = loadAllStrategies();
  const now = new Date().toISOString();

  if (existingId) {
    // Update existing strategy
    const index = strategies.findIndex((s) => s.id === existingId);
    if (index !== -1) {
      const updated: StoredStrategy = {
        ...strategies[index],
        name: state.metadata.name,
        updatedAt: now,
        state,
      };
      const newStrategies = [...strategies];
      newStrategies[index] = updated;
      persistStrategies(newStrategies);
      return updated;
    }
  }

  // Create new strategy
  const newStrategy: StoredStrategy = {
    id: generateId(),
    name: state.metadata.name,
    createdAt: now,
    updatedAt: now,
    state,
  };

  // Enforce max limit
  const newStrategies = [newStrategy, ...strategies].slice(0, MAX_STRATEGIES);
  persistStrategies(newStrategies);
  return newStrategy;
}

/**
 * Delete a strategy by ID
 */
export function deleteStrategy(id: string): boolean {
  const strategies = loadAllStrategies();
  const filtered = strategies.filter((s) => s.id !== id);

  if (filtered.length === strategies.length) {
    return false; // Not found
  }

  persistStrategies(filtered);
  return true;
}

/**
 * Duplicate a strategy
 */
export function duplicateStrategy(id: string): StoredStrategy | null {
  const original = getStrategy(id);
  if (!original) {
    return null;
  }

  const newState: BuilderState = {
    ...original.state,
    metadata: {
      ...original.state.metadata,
      id: generateId(),
      name: `${original.name} (복사본)`,
    },
  };

  return saveStrategy(newState);
}

/**
 * Export strategy as JSON string
 */
export function exportAsJson(id: string): string | null {
  const strategy = getStrategy(id);
  if (!strategy) {
    return null;
  }
  return JSON.stringify(strategy.state, null, 2);
}

/**
 * Import strategy from JSON string
 */
export function importFromJson(json: string): StoredStrategy | null {
  try {
    const state = JSON.parse(json) as BuilderState;
    // Validate required fields
    if (!state.metadata?.name || !state.indicators || !state.entry || !state.exit) {
      return null;
    }
    return saveStrategy(state);
  } catch {
    return null;
  }
}

/**
 * Clear all custom strategies
 */
export function clearAllStrategies(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(STORAGE_KEY);
  }
}

/**
 * Internal: Persist strategies to localStorage
 */
function persistStrategies(strategies: StoredStrategy[]): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(strategies));
  } catch (e) {
    // localStorage is full or unavailable
    if (e instanceof Error && e.name === "QuotaExceededError") {
      // Remove oldest strategies to make room
      const reduced = strategies.slice(0, Math.floor(strategies.length / 2));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(reduced));
    }
  }
}

/**
 * Check if localStorage is available
 */
export function isStorageAvailable(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  try {
    const test = "__storage_test__";
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Get storage usage info
 */
export function getStorageInfo(): { used: number; count: number } {
  if (typeof window === "undefined") {
    return { used: 0, count: 0 };
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const strategies = stored ? (JSON.parse(stored) as StoredStrategy[]) : [];
    return {
      used: stored ? new Blob([stored]).size : 0,
      count: strategies.length,
    };
  } catch {
    return { used: 0, count: 0 };
  }
}
