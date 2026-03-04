"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Download, Loader2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";

interface ExportButtonProps {
  /** Raw YAML content for direct download */
  yamlContent?: string;
  strategyName?: string;
  disabled?: boolean;
  className?: string;
}

export function ExportButton({
  yamlContent,
  strategyName,
  disabled,
  className,
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  // Direct YAML download
  const downloadYaml = useCallback((content: string, filename: string) => {
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

  const handleExport = useCallback(() => {
    if (disabled || isExporting || !yamlContent) return;

    setIsExporting(true);

    try {
      const filename = strategyName
        ? `${strategyName.toLowerCase().replace(/\s+/g, "_")}.kis.yaml`
        : "strategy.kis.yaml";
      downloadYaml(yamlContent, filename);
    } finally {
      setTimeout(() => setIsExporting(false), 500);
    }
  }, [disabled, isExporting, yamlContent, strategyName, downloadYaml]);

  return (
    <button
      onClick={handleExport}
      disabled={disabled || isExporting || !yamlContent}
      className={cn(
        "flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors",
        disabled || isExporting || !yamlContent
          ? "bg-slate-200 text-slate-400 cursor-not-allowed"
          : "bg-primary text-white hover:bg-primary-dark",
        className
      )}
      title={strategyName ? `${strategyName} Export` : "Export"}
    >
      {isExporting ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Download className="w-4 h-4" />
      )}
      <span>Export</span>
    </button>
  );
}

export default ExportButton;
