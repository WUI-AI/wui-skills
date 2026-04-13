#!/usr/bin/env node

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const command = args[0];

const thisFile = fileURLToPath(import.meta.url);
const skillsRoot = path.resolve(path.dirname(thisFile), "..", "skills");
const defaultTarget = path.join(os.homedir(), ".cursor", "skills");

function printUsage() {
  console.log(`Usage:
  npx @wui_ai/wui-skills install <skill-name> [--target <path>]

Examples:
  npx @wui_ai/wui-skills install wui-agent-video
  npx @wui_ai/wui-skills install wui-agent-video --target ~/.cursor/skills`);
}

function parseTarget(inputArgs) {
  const targetFlagIndex = inputArgs.indexOf("--target");
  if (targetFlagIndex === -1) return defaultTarget;
  const value = inputArgs[targetFlagIndex + 1];
  if (!value) {
    throw new Error("--target requires a path value");
  }
  if (value.startsWith("~/")) {
    return path.join(os.homedir(), value.slice(2));
  }
  return path.resolve(value);
}

function installSkill(skillName, targetDir) {
  const from = path.join(skillsRoot, skillName);
  const to = path.join(targetDir, skillName);

  if (!fs.existsSync(from)) {
    throw new Error(`Skill not found: ${skillName}`);
  }

  fs.mkdirSync(targetDir, { recursive: true });
  fs.rmSync(to, { recursive: true, force: true });
  fs.cpSync(from, to, { recursive: true });

  console.log(`Installed ${skillName} to ${to}`);
}

try {
  if (!command || command === "--help" || command === "-h") {
    printUsage();
    process.exit(0);
  }

  if (command !== "install") {
    throw new Error(`Unknown command: ${command}`);
  }

  const skillName = args[1];
  if (!skillName) {
    throw new Error("Missing skill name. Example: install wui-agent-video");
  }

  const targetDir = parseTarget(args);
  installSkill(skillName, targetDir);
} catch (error) {
  console.error(`ERROR: ${error.message}`);
  printUsage();
  process.exit(1);
}
