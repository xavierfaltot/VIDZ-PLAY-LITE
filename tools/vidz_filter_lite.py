#!/usr/bin/env python3
"""Filter a VIDZ PLAY LITE media index.

This block reads the JSON created by vidz_scan_lite.py and writes a smaller
index that can be loaded by the player. It is designed to sit in a chain:

SCAN -> FILTER -> PLAY
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filter a VIDZ PLAY LITE media-index.json.")
    parser.add_argument("--input", default="media-index.json", help="Input media index.")
    parser.add_argument("--output", default="media-index.filtered.json", help="Filtered output index.")
    parser.add_argument("--energy", choices=["low", "medium", "high"], action="append", help="Keep energy class.")
    parser.add_argument("--motion", choices=["slow", "medium", "fast"], action="append", help="Keep motion class.")
    parser.add_argument("--brightness", choices=["dark", "mid", "bright"], action="append", help="Keep brightness class.")
    parser.add_argument("--orientation", choices=["wide", "vertical", "square"], action="append", help="Keep orientation class.")
    parser.add_argument("--tag", action="append", help="Keep videos with this tag. Can be repeated.")
    parser.add_argument("--folder", action="append", help="Keep videos inside folders containing this text.")
    parser.add_argument("--search", help="Keep videos whose name/folder contains this text.")
    parser.add_argument("--min-duration", type=float, default=0, help="Minimum video duration in seconds.")
    parser.add_argument("--max-duration", type=float, default=0, help="Maximum video duration in seconds. 0 disables it.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of videos to keep. 0 disables it.")
    parser.add_argument("--sort", choices=["name", "duration", "energy", "cuts"], default="name", help="Sort output videos.")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order.")
    return parser.parse_args()


def text(value: Any) -> str:
    return str(value or "").lower()


def wanted(value: str, allowed: list[str] | None) -> bool:
    return not allowed or value in allowed


def has_any_tag(item: dict[str, Any], tags: list[str] | None) -> bool:
    if not tags:
      return True
    current = {text(tag) for tag in item.get("tags", [])}
    return any(text(tag) in current for tag in tags)


def has_any_folder(item: dict[str, Any], folders: list[str] | None) -> bool:
    if not folders:
      return True
    folder = text(item.get("folder"))
    return any(text(part) in folder for part in folders)


def matches_search(item: dict[str, Any], query: str | None) -> bool:
    if not query:
      return True
    needle = text(query)
    haystack = f"{text(item.get('name'))} {text(item.get('folder'))} {' '.join(text(tag) for tag in item.get('tags', []))}"
    return needle in haystack


def duration_ok(item: dict[str, Any], min_duration: float, max_duration: float) -> bool:
    duration = float(item.get("duration") or 0)
    if min_duration and duration < min_duration:
      return False
    if max_duration and duration > max_duration:
      return False
    return True


def keep(item: dict[str, Any], args: argparse.Namespace) -> bool:
    return (
      wanted(text(item.get("energy")), args.energy)
      and wanted(text(item.get("motion")), args.motion)
      and wanted(text(item.get("brightness")), args.brightness)
      and wanted(text(item.get("orientation")), args.orientation)
      and has_any_tag(item, args.tag)
      and has_any_folder(item, args.folder)
      and matches_search(item, args.search)
      and duration_ok(item, args.min_duration, args.max_duration)
    )


def sort_key(sort_name: str):
    def key(item: dict[str, Any]):
      if sort_name == "duration":
        return float(item.get("duration") or 0)
      if sort_name == "energy":
        return float(item.get("energyScore") or 0)
      if sort_name == "cuts":
        return int(item.get("cutCount") or 0)
      return text(item.get("name"))
    return key


def main() -> int:
    args = parse_args()
    source = Path(args.input)
    data = json.loads(source.read_text(encoding="utf-8"))
    output = deepcopy(data)
    videos = [item for item in data.get("videos", []) if keep(item, args)]
    videos.sort(key=sort_key(args.sort), reverse=args.reverse)
    if args.limit > 0:
      videos = videos[: args.limit]
    output["videos"] = videos
    output["filter"] = {
      "energy": args.energy or [],
      "motion": args.motion or [],
      "brightness": args.brightness or [],
      "orientation": args.orientation or [],
      "tag": args.tag or [],
      "folder": args.folder or [],
      "search": args.search or "",
      "minDuration": args.min_duration,
      "maxDuration": args.max_duration,
      "limit": args.limit,
      "sort": args.sort,
      "reverse": args.reverse,
      "source": str(source),
    }
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"FILTER OK: {len(videos)}/{len(data.get('videos', []))} videos -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
