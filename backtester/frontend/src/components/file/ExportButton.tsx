"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Download, Loader2, ChevronDown, FileCode, FileText, Archive } from "lucide-react";
import { cn } from "@/lib/utils";
import { exportStrategy, downloadBlob } from "@/lib/api";

type ExportFormat = "yaml" | "python" | "zip";

interface ExportButtonProps {
  /** Strategy ID for backend export (pre-registered strategies) */
  strategyId?: string;
  /** Raw YAML content for direct download (visual builder) */
  yamlContent?: string;
  strategyName?: string;
  disabled?: boolean;
  className?: string;
}

const FORMAT_OPTIONS: { value: ExportFormat; label: string; icon: React.ReactNode; ext: string }[] = [
  {
    value: "yaml",
    label: "YAML (.kis.yaml)",
    icon: <FileText className="w-4 h-4" />,
    ext: ".kis.yaml",
  },
  {
    value: "python",
    label: "Python (.py)",
    icon: <FileCode className="w-4 h-4" />,
    ext: ".py",
  },
  {
    value: "zip",
    label: "ZIP (YAML + Python)",
    icon: <Archive className="w-4 h-4" />,
    ext: ".zip",
  },
];

export function ExportButton({
  strategyId,
  yamlContent,
  strategyName,
  disabled,
  className,
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Direct YAML download (for visual builder / imported strategies)
  const downloadYamlDirect = useCallback((content: string, filename: string) => {
    const blob = new Blob([content], { type: "application/x-yaml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, []);

  const handleExport = async (format: ExportFormat) => {
    if (disabled || isExporting) return;

    setIsExporting(true);
    setError(null);
    setIsOpen(false);

    try {
      // If we have raw YAML content, download directly (no backend call needed for YAML)
      if (yamlContent && format === "yaml") {
        const filename = strategyName
          ? `${strategyName.toLowerCase().replace(/\s+/g, "_")}.kis.yaml`
          : "strategy.kis.yaml";
        downloadYamlDirect(yamlContent, filename);
        return;
      }

      // If we have raw YAML but user wants Python/ZIP, show not supported message
      if (yamlContent && !strategyId) {
        if (format === "python" || format === "zip") {
          setError("Python/ZIP export는 저장된 전략에서만 가능합니다");
          return;
        }
      }

      // Backend export for registered strategies
      if (strategyId && strategyId !== "imported") {
        const blob = await exportStrategy(strategyId, format);
        const option = FORMAT_OPTIONS.find((o) => o.value === format);
        const filename = `${strategyId}${option?.ext || ".kis.yaml"}`;
        downloadBlob(blob, filename);
      } else {
        setError("전략 ID가 없습니다");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Export 실패");
    } finally {
      setIsExporting(false);
    }
  };

  // Determine which formats are available
  const availableFormats = yamlContent && !strategyId
    ? FORMAT_OPTIONS.filter(o => o.value === "yaml") // Only YAML for visual builder
    : FORMAT_OPTIONS;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled || isExporting}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors",
          disabled || isExporting
            ? "bg-slate-200 text-slate-400 cursor-not-allowed"
            : "bg-[#245bee] text-white hover:bg-[#1a47b8]",
          className
        )}
        title={error || (strategyName ? `${strategyName} Export` : "Export")}
      >
        {isExporting ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Download className="w-4 h-4" />
        )}
        <span>Export</span>
        {availableFormats.length > 1 && (
          <ChevronDown className={cn("w-4 h-4 transition-transform", isOpen && "rotate-180")} />
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && !disabled && (
        <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-1 z-50">
          {availableFormats.map((option) => (
            <button
              key={option.value}
              onClick={() => handleExport(option.value)}
              className="w-full flex items-center gap-3 px-4 py-2.5 text-left text-sm text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            >
              {option.icon}
              <span>{option.label}</span>
            </button>
          ))}
        </div>
      )}

      {/* Error tooltip */}
      {error && (
        <div className="absolute right-0 mt-2 px-3 py-2 bg-red-50 text-red-600 text-sm rounded-lg border border-red-200 z-50 whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
}

export default ExportButton;
