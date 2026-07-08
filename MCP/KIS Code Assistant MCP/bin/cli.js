#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const packageRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const isWindows = process.platform === "win32";

function resolveUvCommand() {
  if (process.env.UV_PATH) {
    return process.env.UV_PATH;
  }
  return isWindows ? "uv.exe" : "uv";
}

function checkUv(uvCmd) {
  const result = spawnSync(uvCmd, ["--version"], {
    stdio: "pipe",
    shell: isWindows,
    encoding: "utf-8",
  });
  return result.status === 0;
}

function ensureDependencies(uvCmd) {
  const syncArgs = ["sync", "--frozen"];
  let result = spawnSync(uvCmd, syncArgs, {
    cwd: packageRoot,
    stdio: ["ignore", "pipe", "pipe"],
    shell: isWindows,
    encoding: "utf-8",
  });

  if (result.status !== 0) {
    result = spawnSync(uvCmd, ["sync"], {
      cwd: packageRoot,
      stdio: ["ignore", "pipe", "pipe"],
      shell: isWindows,
      encoding: "utf-8",
    });
  }

  if (result.status !== 0) {
    const message =
      result.stderr?.trim() ||
      result.stdout?.trim() ||
      "Failed to install Python dependencies with uv.";
    process.stderr.write(`${message}\n`);
    process.exit(result.status ?? 1);
  }
}

function printHelp() {
  process.stdout.write(`KIS Code Assistant MCP

Usage:
  @koreainvestment/kis-code-assistant-mcp            Start MCP server (stdio)
  @koreainvestment/kis-code-assistant-mcp --help     Show this help

Requirements:
  - Python 3.12+
  - uv (https://docs.astral.sh/uv/)
`);
}

function main() {
  if (process.argv.includes("--help") || process.argv.includes("-h")) {
    printHelp();
    process.exit(0);
  }

  const uvCmd = resolveUvCommand();
  if (!checkUv(uvCmd)) {
    process.stderr.write(
      "Error: uv is not installed or not in PATH.\n" +
        "Install uv: https://docs.astral.sh/uv/getting-started/installation/\n",
    );
    process.exit(1);
  }

  ensureDependencies(uvCmd);

  const child = spawn(uvCmd, ["run", "server.py", "--stdio"], {
    cwd: packageRoot,
    stdio: "inherit",
    shell: isWindows,
  });

  child.on("error", (error) => {
    process.stderr.write(`Failed to start MCP server: ${error.message}\n`);
    process.exit(1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 0);
  });
}

main();
