"use client";

import { useCallback, useState } from "react";
import { Tag, X } from "lucide-react";
import type { BuilderMetadata } from "@/types/builder";

interface MetadataEditorProps {
  metadata: BuilderMetadata;
  onChange: (updates: Partial<BuilderMetadata>) => void;
}

const CATEGORY_OPTIONS = [
  { value: "trend", label: "추세" },
  { value: "momentum", label: "모멘텀" },
  { value: "mean_reversion", label: "평균회귀" },
  { value: "volatility", label: "변동성" },
  { value: "volume", label: "거래량" },
  { value: "composite", label: "복합" },
  { value: "custom", label: "커스텀" },
];

const SUGGESTED_TAGS = [
  "단기",
  "중기",
  "장기",
  "스윙",
  "데이트레이딩",
  "이평선",
  "오실레이터",
  "캔들스틱",
  "돌파",
  "반전",
];

export function MetadataEditor({ metadata, onChange }: MetadataEditorProps) {
  const [tagInput, setTagInput] = useState("");

  const handleNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange({ name: e.target.value });
    },
    [onChange]
  );

  const handleDescriptionChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      onChange({ description: e.target.value });
    },
    [onChange]
  );

  const handleCategoryChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange({ category: e.target.value });
    },
    [onChange]
  );

  const handleAddTag = useCallback(
    (tag: string) => {
      const trimmed = tag.trim().toLowerCase();
      if (trimmed && !metadata.tags.includes(trimmed)) {
        onChange({ tags: [...metadata.tags, trimmed] });
      }
      setTagInput("");
    },
    [metadata.tags, onChange]
  );

  const handleRemoveTag = useCallback(
    (tag: string) => {
      onChange({ tags: metadata.tags.filter((t) => t !== tag) });
    },
    [metadata.tags, onChange]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" || e.key === ",") {
        e.preventDefault();
        handleAddTag(tagInput);
      }
    },
    [handleAddTag, tagInput]
  );

  return (
    <div className="space-y-4">
      {/* Name */}
      <div>
        <label htmlFor="strategy-name" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          전략 이름 <span className="text-red-500" aria-label="필수">*</span>
        </label>
        <input
          id="strategy-name"
          type="text"
          value={metadata.name}
          onChange={handleNameChange}
          placeholder="예: SMA 골든크로스 + RSI 필터"
          className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
          aria-required="true"
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="strategy-desc" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          설명
        </label>
        <textarea
          id="strategy-desc"
          value={metadata.description}
          onChange={handleDescriptionChange}
          placeholder="전략에 대한 설명을 입력하세요"
          rows={2}
          className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
        />
      </div>

      {/* Category */}
      <div>
        <label htmlFor="strategy-category" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          카테고리
        </label>
        <select
          id="strategy-category"
          value={metadata.category}
          onChange={handleCategoryChange}
          className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {CATEGORY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
          태그
        </label>

        {/* Current Tags */}
        {metadata.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {metadata.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-xs"
              >
                <Tag className="w-3 h-3" />
                {tag}
                <button
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-red-500 transition-colors"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}

        {/* Tag Input */}
        <input
          type="text"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="태그 입력 후 Enter"
          className="w-full px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        {/* Suggested Tags */}
        <div className="mt-2">
          <span className="text-xs text-slate-500">추천:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {SUGGESTED_TAGS.filter((t) => !metadata.tags.includes(t))
              .slice(0, 6)
              .map((tag) => (
                <button
                  key={tag}
                  onClick={() => handleAddTag(tag)}
                  className="px-2 py-0.5 text-xs bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded hover:bg-blue-100 hover:text-blue-600 transition-colors"
                >
                  + {tag}
                </button>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}
