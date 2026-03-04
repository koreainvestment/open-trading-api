/**
 * 파일 Import/Export 타입 정의
 */

export interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
}

export interface TemplateListResponse {
  success: boolean;
  data: Template[];
  total: number;
}

export interface TemplateDetailResponse {
  success: boolean;
  data: {
    id: string;
    name: string;
    yaml: string;
  };
}

export interface ImportResult {
  success: boolean;
  data: {
    id: string;
    name: string;
    category: string;
    description: string;
    definition: Record<string, unknown>;
  };
  message?: string;
}

export interface ValidationResult {
  success: boolean;
  data: {
    id: string;
    name: string;
    valid: boolean;
    errors: string[];
  };
}

export interface KisStrategyFile {
  version: string;
  metadata: {
    name: string;
    description: string;
    author?: string;
    tags: string[];
  };
  strategy: {
    id: string;
    category: string;
    indicators: Array<{
      id: string;
      alias?: string;
      params: Record<string, number>;
    }>;
    entry: {
      logic: "AND" | "OR";
      conditions: Array<{
        indicator: string;
        operator: string;
        compare_to: string | number;
      }>;
    };
    exit: {
      logic: "AND" | "OR";
      conditions: Array<{
        indicator: string;
        operator: string;
        compare_to: string | number;
      }>;
    };
  };
  risk: {
    stop_loss?: { enabled: boolean; percent: number };
    take_profit?: { enabled: boolean; percent: number };
    trailing_stop?: { enabled: boolean; percent: number };
  };
}
