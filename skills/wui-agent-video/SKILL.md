---
name: wui-agent-video
description: Run WUI Agent Video API end-to-end with a bundled script. Use when the user asks to generate a WUI.AI video, check progress, export MP4, or resume from thread_id/task_id. The script handles API chaining and polling for /generate, /progress, /export, and /export/status.
---

# WUI Agent Video

Use this skill when the task is about WUI video generation or export.

## Quick Start

1) Set API token:

```bash
export WUI_AGENT_API_TOKEN="your-token"
```

2) Run full flow (generate -> poll progress -> export -> poll export):

```bash
python scripts/wui_agent_video.py --prompt "Make a 30-second video about ..."
```

3) Return final URL when delivered.

## Token Rule

The script needs `WUI_AGENT_API_TOKEN` or `--token`.

If missing, tell user where to get one:

```text
This WUI.AI video workflow needs an API token. Please get one at https://www.wui.ai/settings/api-tokens, then provide it or set WUI_AGENT_API_TOKEN.
```

Or run with explicit token:

```bash
python scripts/wui_agent_video.py --token "..." --prompt "..."
```

## Endpoints

Default base URL:

- `GET /skill`
- `POST /generate`
- `GET /progress/{thread_id}`
- `POST /export`
- `GET /export/status/{task_id}`

Use custom base URL:

```bash
export WUI_AGENT_VIDEO_BASE_URL="https://llm-server-prod.wui.ai/api/agent/v1/video"
```

## Script usage

### Full workflow

```bash
python scripts/wui_agent_video.py --prompt "Make a 30-second YouTube Shorts video about why people abandon side projects."
```

### Use JSON payload

```bash
python scripts/wui_agent_video.py --input payload.json
```

### Generate and stop before export

```bash
python scripts/wui_agent_video.py --prompt "..." --no-export
```

### Resume from existing thread

```bash
python scripts/wui_agent_video.py --thread-id "<thread_id>"
```

### Progress only

```bash
python scripts/wui_agent_video.py --thread-id "<thread_id>" --progress-only
```

### Export status only

```bash
python scripts/wui_agent_video.py --task-id "<task_id>" --export-status-only
```

### Polling controls

```bash
python scripts/wui_agent_video.py --prompt "..." --poll-interval 5 --max-progress-attempts 120 --max-export-attempts 120
```

## Status Guide

Generate/progress:

```text
queued | generating | ready_for_export | failed
```

Export:

```text
exporting | delivered | failed
```

Stop conditions:
- Progress polling stops when `can_export=true` or status is terminal.
- Export polling stops when status is `delivered` or `failed`.

## Agent workflow

When user asks for a video:

1. Gather prompt (or payload file).
2. Ensure token exists.
3. Run `python scripts/wui_agent_video.py ...`.
4. Relay progress logs to user.
5. Return final MP4 URL.

Do not claim success until export status is `delivered` and URL is present.

## Progress update format

Use concise updates during long polling:
- `Generate task started, thread_id=...`
- `Generating, about 40%, not exportable yet`
- `Export task started, task_id=...`
- `Exporting, about 70%`
- `Done, download URL: ...`
