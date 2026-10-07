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
  process.stdout.write(`KIS Trading MCP

Usage:
  @koreainvestment/kis-trading-mcp            Start MCP server (stdio)
  @koreainvestment/kis-trading-mcp --help     Show this help

The npx entrypoint always starts the server with MCP_TYPE=stdio.
SSE and streamable-http remain available via Docker or uv.

Requirements:
  - Node.js 18+
  - Python 3.11+
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

  if (process.env.MCP_TYPE && process.env.MCP_TYPE !== "stdio") {
    process.stderr.write(
      `npx kis-trading-mcp always uses stdio. Ignoring MCP_TYPE=${process.env.MCP_TYPE}.\n`,
    );
  }

  const child = spawn(uvCmd, ["run", "python", "server.py"], {
    cwd: packageRoot,
    stdio: "inherit",
    shell: isWindows,
    env: {
      ...process.env,
      MCP_TYPE: "stdio",
      ENV: process.env.ENV || "live",
    },
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
