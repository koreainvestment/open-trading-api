"use client";

import { CheckCircle, XCircle, Info, AlertTriangle, Terminal } from "lucide-react";
import type { LogEntry } from "@/types/signal";

interface ExecutionLogProps {
  logs: LogEntry[];
  maxHeight?: string;
}

const LOG_ICONS = {
  info: Info,
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
};

const LOG_STYLES = {
  info: "text-slate-600 dark:text-slate-400",
  success: "text-green-600 dark:text-green-400",
  error: "text-red-600 dark:text-red-400",
  warning: "text-yellow-600 dark:text-yellow-400",
};

export function ExecutionLog({ logs, maxHeight = "200px" }: ExecutionLogProps) {
  if (logs.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900 rounded-lg overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-2 bg-slate-800 border-b border-slate-700">
        <Terminal className="w-4 h-4 text-slate-400" />
        <span className="text-sm font-medium text-slate-300">실행 로그</span>
      </div>
      <div
        className="p-4 font-mono text-sm overflow-y-auto"
        style={{ maxHeight }}
      >
        {logs.map((log, index) => {
          const Icon = LOG_ICONS[log.type] || Info;
          const style = LOG_STYLES[log.type] || LOG_STYLES.info;

          return (
            <div key={index} className={`flex items-start gap-2 ${style} mb-1`}>
              <Icon className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span className="text-slate-500 flex-shrink-0">[{log.timestamp}]</span>
              <span className="break-all">{log.message}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ExecutionLog;
