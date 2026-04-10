---
name: wui-agent-video
description: Use WUI Agent Video API for the generate, progress, export, and export-status workflow with API token authentication. Use when the user asks to create a WUI.AI video, check video generation progress, export an MP4, or integrate with /api/agent/v1/video endpoints.
---

# WUI Agent Video

Use this skill to run WUI.AI's agent video workflow:

1. Generate a video thread.
2. Poll progress until the thread can export.
3. Start MP4 export.
4. Poll export status until the video is delivered.

Prefer the bundled script instead of hand-writing API calls.

## Auth

Set the API token in one of these ways:

```bash
export WUI_AGENT_API_TOKEN="..."
```

If the user does not have an API token, send them to:

```text
https://www.wui.ai/settings/api-tokens
```

Ask them to create or copy a token there, then rerun the script with `WUI_AGENT_API_TOKEN` or `--token`.

or pass it explicitly:

```bash
python scripts/wui_agent_video.py --token "..." --prompt "..."
```

The API uses:

```text
Authorization: <api_token>
```

Required scope:

```text
video.generate
```

## Endpoints

Default API base:

```text
https://llm-server.wui.ai/api/agent/v1/video
```

Endpoints:

- `GET /skill`
- `POST /generate`
- `GET /progress/{thread_id}`
- `POST /export`
- `GET /export/status/{task_id}`

Override the base URL with:

```bash
export WUI_AGENT_VIDEO_BASE_URL="https://.../api/agent/v1/video"
```

or:

```bash
python scripts/wui_agent_video.py --base-url "https://.../api/agent/v1/video" --prompt "..."
```

## Script usage

Run the full workflow:

```bash
python scripts/wui_agent_video.py --prompt "Make a 30-second YouTube Shorts video about why people abandon side projects."
```

With an input JSON payload:

```bash
python scripts/wui_agent_video.py --input payload.json
```

Only generate and stop before export:

```bash
python scripts/wui_agent_video.py --prompt "..." --no-export
```

Resume export from an existing thread:

```bash
python scripts/wui_agent_video.py --thread-id "<thread_id>"
```

Check progress only:

```bash
python scripts/wui_agent_video.py --thread-id "<thread_id>" --progress-only
```

Check export status only:

```bash
python scripts/wui_agent_video.py --task-id "<task_id>" --export-status-only
```

## Expected statuses

Generate/progress statuses:

```text
queued | generating | ready_for_export | failed
```

Export statuses:

```text
exporting | delivered | failed
```

## Agent workflow

When the user asks to create a video:

1. Collect the minimum viable prompt or source material.
2. Ask for missing API token only if `WUI_AGENT_API_TOKEN` is absent.
   - If the user does not have a token, tell them to get one at `https://www.wui.ai/settings/api-tokens`.
3. Run `scripts/wui_agent_video.py` with the prompt or payload.
4. Report:
   - `thread_id`
   - generation status
   - `task_id`
   - export status
   - delivered MP4 URL, if available

Do not claim the video is exported until export status is `delivered` and the response includes a usable `data.url`.
