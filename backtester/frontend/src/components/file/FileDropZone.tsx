"use client";

import { useCallback, useState } from "react";
import { Upload, FileText, AlertCircle, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { validateFile } from "@/lib/api";
import type { ValidationResult } from "@/types";

interface FileDropZoneProps {
  onFileSelect: (file: File, content: string) => void;
  onValidationResult?: (result: ValidationResult) => void;
  className?: string;
}

export function FileDropZone({
  onFileSelect,
  onValidationResult,
  className,
}: FileDropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleFile = useCallback(
    async (file: File) => {
      // 확장자 검증
      if (!file.name.match(/\.(yaml|yml|kis\.yaml)$/i)) {
        setError("YAML 파일만 업로드할 수 있습니다 (.yaml, .yml)");
        return;
      }

      setError(null);
      setIsValidating(true);
      setSelectedFile(file.name);

      try {
        // 파일 내용 읽기
        const content = await file.text();

        // 서버 검증
        const result = await validateFile(file);
        onValidationResult?.(result);

        if (result.success && result.data.valid) {
          onFileSelect(file, content);
        } else {
          setError(result.data.errors.join(", ") || "파일 검증 실패");
        }
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "파일 처리 중 오류 발생"
        );
      } finally {
        setIsValidating(false);
      }
    },
    [onFileSelect, onValidationResult]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={cn(
        "relative border-2 border-dashed rounded-xl p-8 transition-all",
        isDragging
          ? "border-[#245bee] bg-[#245bee]/5"
          : "border-slate-300 dark:border-slate-600 hover:border-slate-400",
        isValidating && "opacity-50 pointer-events-none",
        className
      )}
    >
      <input
        type="file"
        accept=".yaml,.yml"
        onChange={handleInputChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        disabled={isValidating}
      />

      <div className="flex flex-col items-center text-center">
        {isValidating ? (
          <>
            <div className="w-12 h-12 rounded-full bg-[#245bee]/10 flex items-center justify-center mb-4 animate-pulse">
              <FileText className="w-6 h-6 text-[#245bee]" />
            </div>
            <p className="text-slate-600 dark:text-slate-400">
              검증 중... <span className="font-mono">{selectedFile}</span>
            </p>
          </>
        ) : error ? (
          <>
            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4">
              <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <p className="text-red-600 dark:text-red-400 mb-2">{error}</p>
            <p className="text-sm text-slate-500">다시 시도하세요</p>
          </>
        ) : selectedFile ? (
          <>
            <div className="w-12 h-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mb-4">
              <Check className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <p className="text-emerald-600 dark:text-emerald-400 font-medium mb-1">
              파일 로드 완료
            </p>
            <p className="text-sm text-slate-500 font-mono">{selectedFile}</p>
          </>
        ) : (
          <>
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
              <Upload className="w-6 h-6 text-slate-500" />
            </div>
            <p className="text-slate-700 dark:text-slate-300 font-medium mb-1">
              .kis.yaml 파일을 드래그하거나 클릭하여 선택
            </p>
            <p className="text-sm text-slate-500">
              전략 파일을 업로드하면 자동으로 검증됩니다
            </p>
          </>
        )}
      </div>
    </div>
  );
}

export default FileDropZone;
