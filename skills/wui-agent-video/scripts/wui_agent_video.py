#!/usr/bin/env python3
"""Run the WUI Agent Video generate/progress/export workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://llm-server-prod.wui.ai/api/agent/v1/video"
GENERATE_TERMINAL_STATUSES = {"ready_for_export", "failed"}
EXPORT_TERMINAL_STATUSES = {"delivered", "failed"}

GENERATE_STATUS_LABELS = {
    "queued": "queued",
    "generating": "generating",
    "ready_for_export": "ready for export",
    "failed": "generation failed",
}

EXPORT_STATUS_LABELS = {
    "exporting": "exporting",
    "delivered": "delivered",
    "failed": "export failed",
}


class ApiError(RuntimeError):
    pass


def request_json(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    data = None
    headers = {
        "Authorization": token,
        "Accept": "application/json",
    }

    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiError(f"{method} {url} failed: HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise ApiError(f"{method} {url} failed: {exc}") from exc

    if not body:
        return {}

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError as exc:
        raise ApiError(f"{method} {url} returned non-JSON: {body[:500]}") from exc

    if not isinstance(parsed, dict):
        raise ApiError(f"{method} {url} returned unexpected JSON: {parsed!r}")

    return parsed


def get_nested(data: dict[str, Any], *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("--input must point to a JSON object")
        return payload

    if args.prompt:
        return {"prompt": args.prompt}

    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if text:
            try:
                payload = json.loads(text)
                if isinstance(payload, dict):
                    return payload
            except json.JSONDecodeError:
                return {"prompt": text}

    raise ValueError("Provide --prompt, --input, --thread-id, or JSON/text on stdin")


def extract_thread_id(response: dict[str, Any]) -> str | None:
    for path in [
        ("data", "thread_id"),
        ("data", "threadId"),
        ("thread_id",),
        ("threadId",),
    ]:
        value = get_nested(response, *path)
        if value:
            return str(value)
    return None


def extract_task_id(response: dict[str, Any]) -> str | None:
    for path in [
        ("data", "task_id"),
        ("data", "taskId"),
        ("task_id",),
        ("taskId",),
    ]:
        value = get_nested(response, *path)
        if value:
            return str(value)
    return None


def extract_status(response: dict[str, Any]) -> str | None:
    for path in [
        ("data", "status"),
        ("status",),
    ]:
        value = get_nested(response, *path)
        if value is not None:
            return str(value)
    return None


def extract_can_export(response: dict[str, Any]) -> bool:
    for path in [
        ("data", "can_export"),
        ("data", "canExport"),
        ("can_export",),
        ("canExport",),
    ]:
        value = get_nested(response, *path)
        if isinstance(value, bool):
            return value
    return extract_status(response) == "ready_for_export"


def extract_url(response: dict[str, Any]) -> str | None:
    for path in [
        ("data", "url"),
        ("url",),
    ]:
        value = get_nested(response, *path)
        if value:
            return str(value)
    return None


def extract_progress_value(response: dict[str, Any]) -> int | float | None:
    for path in [
        ("data", "progress"),
        ("data", "process"),
        ("progress",),
        ("process",),
    ]:
        value = get_nested(response, *path)
        if isinstance(value, (int, float)):
            return value
    return None


def format_progress(value: int | float | None) -> str:
    if value is None:
        return "unknown progress"
    if 0 <= value <= 1:
        value = value * 100
    return f"{round(value)}%"


def format_status(status: str | None, labels: dict[str, str]) -> str:
    if not status:
        return "unknown status"
    label = labels.get(status)
    return f"{label} ({status})" if label else status


def print_json(label: str, payload: dict[str, Any]) -> None:
    print(f"\n## {label}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def poll_progress(base_url: str, token: str, thread_id: str, interval: int, max_attempts: int) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for attempt in range(1, max_attempts + 1):
        last = request_json("GET", f"{base_url}/progress/{thread_id}", token)
        status = extract_status(last)
        can_export = extract_can_export(last)
        progress = extract_progress_value(last)
        print(
            "[WUI Agent Video] "
            f"Progress check {attempt}: generation is {format_status(status, GENERATE_STATUS_LABELS)}, "
            f"{format_progress(progress)}, "
            f"{'export is available' if can_export else 'not exportable yet'}."
        )
        sys.stdout.flush()
        if can_export or status in GENERATE_TERMINAL_STATUSES:
            return last
        time.sleep(interval)
    raise TimeoutError(f"progress polling timed out after {max_attempts} attempts")


def poll_export(base_url: str, token: str, task_id: str, interval: int, max_attempts: int) -> dict[str, Any]:
    last: dict[str, Any] = {}
    for attempt in range(1, max_attempts + 1):
        last = request_json("GET", f"{base_url}/export/status/{task_id}", token)
        status = extract_status(last)
        url = extract_url(last)
        progress = extract_progress_value(last)
        print(
            "[WUI Agent Video] "
            f"Export check {attempt}: export is {format_status(status, EXPORT_STATUS_LABELS)}, "
            f"{format_progress(progress)}"
            f"{', download URL is available.' if url else '.'}"
        )
        sys.stdout.flush()
        if status in EXPORT_TERMINAL_STATUSES:
            return last
        time.sleep(interval)
    raise TimeoutError(f"export polling timed out after {max_attempts} attempts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.getenv("WUI_AGENT_VIDEO_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--token", default=os.getenv("WUI_AGENT_API_TOKEN"))
    parser.add_argument("--prompt")
    parser.add_argument("--input", help="Path to a JSON request payload for /generate")
    parser.add_argument("--thread-id", help="Existing thread_id to resume from")
    parser.add_argument("--task-id", help="Existing export task_id")
    parser.add_argument("--progress-only", action="store_true")
    parser.add_argument("--export-status-only", action="store_true")
    parser.add_argument("--no-export", action="store_true")
    parser.add_argument("--poll-interval", type=int, default=5)
    parser.add_argument("--max-progress-attempts", type=int, default=120)
    parser.add_argument("--max-export-attempts", type=int, default=120)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    if not args.token:
        print(
            "Missing API token. Get one at https://www.wui.ai/settings/api-tokens, "
            "then set WUI_AGENT_API_TOKEN or pass --token.",
            file=sys.stderr,
        )
        return 2

    try:
      if args.export_status_only:
          if not args.task_id:
              raise ValueError("--export-status-only requires --task-id")
          status = request_json("GET", f"{base_url}/export/status/{args.task_id}", args.token)
          print_json("export_status", status)
          return 0

      if args.progress_only:
          if not args.thread_id:
              raise ValueError("--progress-only requires --thread-id")
          progress = request_json("GET", f"{base_url}/progress/{args.thread_id}", args.token)
          print_json("progress", progress)
          return 0

      thread_id = args.thread_id
      if not thread_id:
          payload = load_payload(args)
          print("[WUI Agent Video] Step 1: creating generation task.")
          sys.stdout.flush()
          generated = request_json("POST", f"{base_url}/generate", args.token, payload)
          print_json("generate", generated)
          thread_id = extract_thread_id(generated)
          if not thread_id:
              raise ApiError("Could not find thread_id in /generate response")
          print(f"[WUI Agent Video] Generation task created, thread_id={thread_id}.")
          sys.stdout.flush()

      print("[WUI Agent Video] Step 2: polling generation progress until export is available.")
      sys.stdout.flush()
      progress = poll_progress(
          base_url,
          args.token,
          thread_id,
          args.poll_interval,
          args.max_progress_attempts,
      )
      print_json("progress_final", progress)

      if not extract_can_export(progress):
          raise ApiError(f"Thread is not exportable. status={extract_status(progress)}")

      if args.no_export:
          print(f"\nReady for export: thread_id={thread_id}")
          return 0

      print("[WUI Agent Video] Step 3: creating MP4 export task.")
      sys.stdout.flush()
      exported = request_json("POST", f"{base_url}/export", args.token, {"thread_id": thread_id})
      print_json("export", exported)
      task_id = extract_task_id(exported)
      if not task_id:
          raise ApiError("Could not find task_id in /export response")
      print(f"[WUI Agent Video] Export task created, task_id={task_id}.")
      sys.stdout.flush()

      print("[WUI Agent Video] Step 4: polling export progress until delivery.")
      sys.stdout.flush()
      export_status = poll_export(
          base_url,
          args.token,
          task_id,
          args.poll_interval,
          args.max_export_attempts,
      )
      print_json("export_final", export_status)

      url = extract_url(export_status)
      if extract_status(export_status) == "delivered" and url:
          print(f"\n[WUI Agent Video] Video export delivered: {url}")
          return 0

      raise ApiError(f"Export did not deliver a URL. status={extract_status(export_status)}")
    except (ApiError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
