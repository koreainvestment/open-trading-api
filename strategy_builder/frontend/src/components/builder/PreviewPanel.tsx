"use client";

import { useState, useCallback, useEffect } from "react";
import {
  Copy,
  Check,
  FileText,
  Download,
  Code2,
  Pencil,
  Eye,
  ChevronDown,
  ChevronUp,
  Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";

type PreviewTab = "yaml" | "python";

interface PreviewPanelProps {
  yamlContent: string;
  pythonContent?: string;
  pythonLoading?: boolean;
  pythonError?: string;
  onExport?: () => void;
  onExportPython?: () => void;
  onRequestPython?: () => void;
  /** Enable edit mode toggle */
  editable?: boolean;
  /** Callback when YAML is edited (only when editable=true) */
  onYamlChange?: (yaml: string) => void;
  /** Collapsible mode (for mobile / space-saving) */
  collapsible?: boolean;
  /** Default collapsed state */
  defaultCollapsed?: boolean;
}

// ============================================================
// Simple YAML syntax highlighting
// ============================================================

function highlightYaml(content: string): React.ReactNode[] {
  return content.split("\n").map((line, i) => {
    if (line.trimStart().startsWith("#")) {
      return (
        <span key={i} className="text-slate-500 italic">
          {line}
          {"\n"}
        </span>
      );
    }

    const keyMatch = line.match(/^(\s*)([\w_-]+)(\s*:\s*)(.*)/);
    if (keyMatch) {
      const [, indent, key, colon, value] = keyMatch;
      return (
        <span key={i}>
          {indent}
          <span className="text-cyan-400">{key}</span>
          <span className="text-slate-400">{colon}</span>
          {highlightYamlValue(value)}
          {"\n"}
        </span>
      );
    }

    const listMatch = line.match(/^(\s*)(- )(.*)/);
    if (listMatch) {
      const [, indent, dash, value] = listMatch;
      return (
        <span key={i}>
          {indent}
          <span className="text-slate-400">{dash}</span>
          {highlightYamlValue(value)}
          {"\n"}
        </span>
      );
    }

    return (
      <span key={i}>
        {line}
        {"\n"}
      </span>
    );
  });
}

function highlightYamlValue(value: string): React.ReactNode {
  if (!value) return null;

  if (/^["'].*["']$/.test(value)) {
    return <span className="text-green-400">{value}</span>;
  }
  if (/^-?\d+(\.\d+)?$/.test(value.trim())) {
    return <span className="text-amber-400">{value}</span>;
  }
  if (/^(true|false)$/i.test(value.trim())) {
    return <span className="text-purple-400">{value}</span>;
  }
  if (/^(AND|OR|cross_above|cross_below|greater_than|less_than|greater_equal|less_equal|equals)$/.test(value.trim())) {
    return <span className="text-orange-400 font-medium">{value}</span>;
  }

  const inlineKV = value.match(/^([\w_-]+)(\s*:\s*)(.*)/);
  if (inlineKV) {
    const [, k, c, v] = inlineKV;
    return (
      <>
        <span className="text-cyan-400">{k}</span>
        <span className="text-slate-400">{c}</span>
        {highlightYamlValue(v)}
      </>
    );
  }

  return <span className="text-slate-200">{value}</span>;
}

// ============================================================
// Simple Python syntax highlighting
// ============================================================

function highlightPython(content: string): React.ReactNode[] {
  return content.split("\n").map((line, i) => {
    // Comments
    if (line.trimStart().startsWith("#")) {
      return (
        <span key={i} className="text-slate-500 italic">
          {line}
          {"\n"}
        </span>
      );
    }

    // Keywords
    let highlighted = line;
    const parts: React.ReactNode[] = [];
    const keywords = /\b(def|class|if|elif|else|return|import|from|and|or|not|True|False|None|self|async|await|try|except|raise|with|as|for|in|while|break|continue|pass|lambda|yield)\b/g;
    const builtins = /\b(print|len|range|int|float|str|list|dict|set|tuple|bool|type|super|isinstance|getattr|setattr|hasattr|property)\b/g;
    const decorators = /^(\s*)(@\w+)/;
    const strings = /(["'])(?:(?=(\\?))\2.)*?\1/g;

    let lastIndex = 0;
    const tokens: { start: number; end: number; className: string; text: string }[] = [];

    // Find strings first (to avoid highlighting keywords in strings)
    let strMatch;
    while ((strMatch = strings.exec(highlighted)) !== null) {
      tokens.push({
        start: strMatch.index,
        end: strMatch.index + strMatch[0].length,
        className: "text-green-400",
        text: strMatch[0],
      });
    }

    // Decorator
    const decMatch = highlighted.match(decorators);
    if (decMatch) {
      tokens.push({
        start: (decMatch[1] || "").length,
        end: (decMatch[1] || "").length + decMatch[2].length,
        className: "text-yellow-400",
        text: decMatch[2],
      });
    }

    // Keywords
    let kwMatch;
    while ((kwMatch = keywords.exec(highlighted)) !== null) {
      const inString = tokens.some(t => kwMatch!.index >= t.start && kwMatch!.index < t.end);
      if (!inString) {
        tokens.push({
          start: kwMatch.index,
          end: kwMatch.index + kwMatch[0].length,
          className: "text-purple-400 font-medium",
          text: kwMatch[0],
        });
      }
    }

    // Builtins
    let biMatch;
    while ((biMatch = builtins.exec(highlighted)) !== null) {
      const inString = tokens.some(t => biMatch!.index >= t.start && biMatch!.index < t.end);
      const inKw = tokens.some(t => t.className.includes("purple") && biMatch!.index >= t.start && biMatch!.index < t.end);
      if (!inString && !inKw) {
        tokens.push({
          start: biMatch.index,
          end: biMatch.index + biMatch[0].length,
          className: "text-cyan-400",
          text: biMatch[0],
        });
      }
    }

    // Sort by position
    tokens.sort((a, b) => a.start - b.start);

    // Build parts
    for (const token of tokens) {
      if (token.start > lastIndex) {
        parts.push(<span key={`t-${i}-${lastIndex}`} className="text-slate-200">{highlighted.slice(lastIndex, token.start)}</span>);
      }
      parts.push(<span key={`t-${i}-${token.start}`} className={token.className}>{token.text}</span>);
      lastIndex = token.end;
    }

    if (lastIndex < highlighted.length) {
      parts.push(<span key={`t-${i}-end`} className="text-slate-200">{highlighted.slice(lastIndex)}</span>);
    }

    return (
      <span key={i}>
        {parts.length > 0 ? parts : <span className="text-slate-200">{line}</span>}
        {"\n"}
      </span>
    );
  });
}

// ============================================================
// PreviewPanel Component
// ============================================================

export function PreviewPanel({
  yamlContent,
  pythonContent,
  pythonLoading = false,
  pythonError,
  onExport,
  onExportPython,
  onRequestPython,
  editable = false,
  onYamlChange,
  collapsible = false,
  defaultCollapsed = false,
}: PreviewPanelProps) {
  const [activeTab, setActiveTab] = useState<PreviewTab>("yaml");
  const [copied, setCopied] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedYaml, setEditedYaml] = useState(yamlContent);
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  // Auto-fetch Python when tab is active and content is reset/empty
  useEffect(() => {
    if (activeTab === "python" && !pythonContent && !pythonLoading && !pythonError && onRequestPython) {
      onRequestPython();
    }
  }, [activeTab, pythonContent, pythonLoading, pythonError, onRequestPython]);

  const handleEditToggle = useCallback(() => {
    if (!isEditMode) {
      setEditedYaml(yamlContent);
    }
    setIsEditMode(!isEditMode);
  }, [isEditMode, yamlContent]);

  const handleYamlEdit = useCallback((value: string) => {
    setEditedYaml(value);
    onYamlChange?.(value);
  }, [onYamlChange]);

  const handleCopy = useCallback(() => {
    const contentToCopy = activeTab === "yaml"
      ? (isEditMode ? editedYaml : yamlContent)
      : (pythonContent || "");
    if (contentToCopy) {
      navigator.clipboard.writeText(contentToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [activeTab, yamlContent, editedYaml, isEditMode, pythonContent]);

  const handleTabSwitch = useCallback((tab: PreviewTab) => {
    setActiveTab(tab);
    if (tab === "python" && !pythonContent && !pythonLoading && onRequestPython) {
      onRequestPython();
    }
  }, [pythonContent, pythonLoading, onRequestPython]);

  const displayContent = activeTab === "yaml"
    ? (isEditMode ? editedYaml : yamlContent)
    : pythonContent;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-1">
          {/* Collapse Toggle */}
          {collapsible && (
            <button
              onClick={() => setIsCollapsed((prev) => !prev)}
              className="p-1.5 rounded-md text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus-ring"
              aria-label={isCollapsed ? "미리보기 펼치기" : "미리보기 접기"}
              aria-expanded={!isCollapsed}
            >
              {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
            </button>
          )}

          {/* Tab Toggle: YAML / Python */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 rounded-md p-0.5">
            <button
              onClick={() => handleTabSwitch("yaml")}
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors",
                activeTab === "yaml"
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              )}
            >
              <FileText className="w-3 h-3" aria-hidden="true" />
              YAML
            </button>
            <button
              onClick={() => handleTabSwitch("python")}
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors",
                activeTab === "python"
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              )}
            >
              <Code2 className="w-3 h-3" aria-hidden="true" />
              Python
            </button>
          </div>

          {/* Edit Mode Toggle (YAML only) */}
          {editable && !isCollapsed && activeTab === "yaml" && (
            <button
              onClick={handleEditToggle}
              aria-label={isEditMode ? "미리보기 모드로 전환" : "편집 모드로 전환"}
              className={cn(
                "flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium transition-colors focus-ring",
                isEditMode
                  ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
              )}
            >
              {isEditMode ? (
                <>
                  <Eye className="w-3 h-3" aria-hidden="true" />
                  미리보기
                </>
              ) : (
                <>
                  <Pencil className="w-3 h-3" aria-hidden="true" />
                  편집
                </>
              )}
            </button>
          )}
        </div>

        {/* Actions */}
        {!isCollapsed && (
          <div className="flex items-center gap-1">
            <button
              onClick={handleCopy}
              disabled={!displayContent}
              aria-label={copied ? "복사 완료" : "클립보드에 복사"}
              className="flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 focus-ring"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-green-500" aria-hidden="true" />
                  <span className="text-green-600" role="status">복사됨</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" aria-hidden="true" />
                  <span>복사</span>
                </>
              )}
            </button>
            {activeTab === "yaml" && onExport && (
              <button
                onClick={onExport}
                disabled={!yamlContent}
                aria-label="YAML 파일 내보내기"
                className="flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 focus-ring"
              >
                <Download className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Export</span>
              </button>
            )}
            {activeTab === "python" && onExportPython && (
              <button
                onClick={onExportPython}
                disabled={!pythonContent}
                aria-label="Python 파일 내보내기"
                className="flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-colors text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 focus-ring"
              >
                <Download className="w-3.5 h-3.5" aria-hidden="true" />
                <span>Export</span>
              </button>
            )}
          </div>
        )}
      </div>

      {/* Content - collapsible */}
      {!isCollapsed && (
        <>
          <div className="flex-1 overflow-hidden rounded-lg border border-slate-200 dark:border-slate-700">
            {activeTab === "python" && pythonLoading ? (
              <div className="h-full flex items-center justify-center bg-slate-900 min-h-[200px]">
                <div className="text-center text-slate-400">
                  <Loader2 className="w-6 h-6 mx-auto mb-2 animate-spin" aria-hidden="true" />
                  <p className="text-xs">Python 코드 생성 중...</p>
                </div>
              </div>
            ) : activeTab === "python" && pythonError ? (
              <div className="h-full flex items-center justify-center bg-slate-900 min-h-[200px]">
                <div className="text-center text-red-400">
                  <Code2 className="w-8 h-8 mx-auto mb-2 opacity-50" aria-hidden="true" />
                  <p className="text-xs">코드 생성 실패</p>
                  <p className="text-xs mt-1 text-slate-500">{pythonError}</p>
                </div>
              </div>
            ) : activeTab === "python" && !pythonContent ? (
              <div className="h-full flex items-center justify-center bg-slate-900 min-h-[200px]">
                <div className="text-center text-slate-400">
                  <Code2 className="w-8 h-8 mx-auto mb-2 opacity-50" aria-hidden="true" />
                  <p className="text-xs">진입/청산 조건을 추가하면</p>
                  <p className="text-xs">Python 코드가 생성됩니다</p>
                </div>
              </div>
            ) : displayContent ? (
              activeTab === "yaml" && isEditMode ? (
                <textarea
                  value={editedYaml}
                  onChange={(e) => handleYamlEdit(e.target.value)}
                  className="w-full h-full p-4 bg-slate-900 text-slate-100 text-xs font-mono resize-none focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                  spellCheck={false}
                  aria-label="YAML 편집기"
                />
              ) : (
                <pre className="h-full overflow-auto p-4 bg-slate-900 text-slate-100 text-xs font-mono whitespace-pre-wrap">
                  <code>
                    {activeTab === "yaml" ? highlightYaml(displayContent) : highlightPython(displayContent)}
                  </code>
                </pre>
              )
            ) : (
              <div className="h-full flex items-center justify-center bg-slate-50 dark:bg-slate-800/50">
                <div className="text-center text-slate-400">
                  <FileText className="w-10 h-10 mx-auto mb-2 opacity-50" aria-hidden="true" />
                  <p className="text-sm">지표와 조건을 추가하면</p>
                  <p className="text-sm">미리보기가 표시됩니다</p>
                </div>
              </div>
            )}
          </div>

          {/* Edit Mode Warning */}
          {isEditMode && activeTab === "yaml" && (
            <div className="mt-2 px-3 py-2 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-xs text-amber-700 dark:text-amber-400" role="alert">
              <strong>편집 모드:</strong> 직접 수정한 YAML은 비주얼 빌더와 동기화되지 않습니다.
            </div>
          )}
        </>
      )}

      {/* Collapsed indicator */}
      {isCollapsed && (
        <div className="py-2 text-center text-xs text-slate-400">
          미리보기가 접혀있습니다
        </div>
      )}
    </div>
  );
}
