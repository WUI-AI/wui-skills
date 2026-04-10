# wui-skills

WUI.AI agent skills.

This README is written for AI agents and automation tools that need to install and use WUI.AI skills.

<p>
  <a href="./README.zh-CN.md">
    <img alt="中文说明" src="https://img.shields.io/badge/中文说明-zh--CN-blue" />
  </a>
</p>

## Purpose

This repository contains WUI.AI skills for agents. The current video skill is:

```text
wui-agent-video
```

Use it when the user asks an agent to create, plan, script, storyboard, edit, export, or check progress for a WUI.AI video.

## Install

Install the video skill globally:

```bash
npx skills add https://github.com/WUI-AI/wui-skills -g --skill wui-agent-video
```

Meaning:

- `https://github.com/WUI-AI/wui-skills` is the skill repository.
- `--skill wui-agent-video` selects the `wui-agent-video` skill from this repository. It does not rename the skill.
- `-g` installs it globally in the user's skills directory so it is available across projects.

If the installer asks for an installation method, choose **Symlink** when available. Symlink keeps one canonical copy and makes updates easier. Use Copy only when symlinks are not supported.

For non-interactive installs:

```bash
npx skills add https://github.com/WUI-AI/wui-skills -g --skill wui-agent-video -y
```

## Use

After installation, invoke the skill by name:

```text
Use wui-agent-video to turn this idea into a 30-second YouTube Shorts script and storyboard: ...
```

```text
Use wui-agent-video to generate a WUI.AI video and export the MP4.
```

The skill includes a script for the WUI Agent Video API workflow:

```bash
python scripts/wui_agent_video.py --prompt "Make a 30-second video about ..."
```

Set the API token before running the script:

```bash
export WUI_AGENT_API_TOKEN="..."
```

