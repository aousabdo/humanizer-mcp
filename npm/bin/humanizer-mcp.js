#!/usr/bin/env node

/**
 * humanizer-mcp — thin Node launcher for the Python package.
 *
 * Runner preference order:
 *   1. uvx humanizer-mcp         (zero install, preferred)
 *   2. pipx run humanizer-mcp    (if uv is unavailable)
 *   3. python3 -m humanizer_mcp  (if already pip-installed)
 *
 * All CLI arguments are forwarded verbatim. Signals are relayed so that
 * Ctrl-C and termination from the parent MCP client kill the child cleanly.
 */

"use strict";

const { spawnSync, spawn } = require("node:child_process");

const args = process.argv.slice(2);
const PY_MODULE = "humanizer_mcp";
const PY_PACKAGE = "humanizer-mcp";

function commandExists(cmd) {
  const checker = process.platform === "win32" ? "where" : "which";
  const result = spawnSync(checker, [cmd], { stdio: "ignore" });
  return result.status === 0;
}

function pythonModuleExists(python) {
  const result = spawnSync(python, ["-c", `import ${PY_MODULE}`], {
    stdio: "ignore",
  });
  return result.status === 0;
}

function run(command, commandArgs) {
  const child = spawn(command, commandArgs, {
    stdio: "inherit",
    shell: false,
  });

  child.on("error", (err) => {
    console.error(`humanizer-mcp: failed to launch ${command}: ${err.message}`);
    process.exit(1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
    } else {
      process.exit(code ?? 0);
    }
  });

  for (const sig of ["SIGINT", "SIGTERM"]) {
    process.on(sig, () => {
      if (!child.killed) child.kill(sig);
    });
  }
}

function main() {
  if (commandExists("uvx")) {
    return run("uvx", [PY_PACKAGE, ...args]);
  }

  if (commandExists("pipx")) {
    return run("pipx", ["run", PY_PACKAGE, ...args]);
  }

  for (const py of ["python3", "python"]) {
    if (commandExists(py) && pythonModuleExists(py)) {
      return run(py, ["-m", PY_MODULE, ...args]);
    }
  }

  console.error(
    [
      "humanizer-mcp: could not find a Python runtime to launch the server.",
      "",
      "Install one of the following, then re-run:",
      "  - uv           (recommended)   https://docs.astral.sh/uv/",
      "  - pipx                         https://pipx.pypa.io/",
      "  - or: pip install humanizer-mcp",
      "",
    ].join("\n"),
  );
  process.exit(127);
}

main();
