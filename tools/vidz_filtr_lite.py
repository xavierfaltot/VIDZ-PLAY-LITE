#!/usr/bin/env python3
"""FILTR block for VIDZ PLAY LITE.

FILTR reads the JSON created by SCAN, filters clips, and can organise an
export card. It is designed for a physical chain:

SCAN -> FILTR -> PLAY
"""

from __future__ import annotations

import argparse
import json
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filter and organise a VIDZ PLAY LITE media index.")
    parser.add_argument("--input", default="media-index.json", help="Input media index.")
    parser.add_argument("--output", default="media-index.filtr.json", help="Filtered output index.")
    parser.add_argument("--set-name", default="SET_001", help="Name used for organised export folders.")
    parser.add_argument("--export-dir", help="Optional export card/folder root.")
    parser.add_argument("--copy-media", action="store_true", help="Copy selected media files into the export folder.")
    parser.add_argument("--copy-thumbs", action="store_true", help="Copy cached thumbnails into the export folder.")
    parser.add_argument("--organise-by", choices=["flat", "energy", "motion", "brightness", "orientation", "folder"], default="energy", help="How copied files are grouped.")
    parser.add_argument("--player-url", default="", help="URL prefix for copied media in the exported player index.")
    parser.add_argument("--energy", choices=["low", "medium", "high"], action="append", help="Keep energy class.")
    parser.add_argument("--motion", choices=["slow", "medium", "fast"], action="append", help="Keep motion class.")
    parser.add_argument("--brightness", choices=["dark", "mid", "bright"], action="append", help="Keep brightness class.")
    parser.add_argument("--orientation", choices=["wide", "vertical", "square"], action="append", help="Keep orientation class.")
    parser.add_argument("--tag", action="append", help="Keep videos with this tag. Can be repeated.")
    parser.add_argument("--folder", action="append", help="Keep videos inside folders containing this text.")
    parser.add_argument("--search", help="Keep videos whose name/folder/tags contain this text.")
    parser.add_argument("--min-duration", type=float, default=0, help="Minimum video duration in seconds.")
    parser.add_argument("--max-duration", type=float, default=0, help="Maximum video duration in seconds. 0 disables it.")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of videos to keep. 0 disables it.")
    parser.add_argument("--sort", choices=["name", "duration", "energy", "cuts"], default="name", help="Sort output videos.")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order.")
    return parser.parse_args()


def text(value: Any) -> str:
    return str(value or "").lower()


def safe_name(value: str) -> str:
    clean = "".join(char if char.isalnum() or char in "-_." else "_" for char in str(value).strip())
    return clean.strip("._") or "UNTITLED"


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


def group_for(item: dict[str, Any], organise_by: str) -> str:
    if organise_by == "flat":
      return "CLIPS"
    if organise_by == "folder":
      return safe_name(item.get("folder") or "ROOT")
    return safe_name(item.get(organise_by) or "UNKNOWN")


def file_url(prefix: str, relative: Path) -> str:
    rel = quote(relative.as_posix())
    if not prefix:
      return rel
    return f"{prefix.rstrip('/')}/{rel}"


def copy_unique(source: Path, destination_dir: Path) -> Path | None:
    if not source.exists() or not source.is_file():
      return None
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name
    if destination.exists() and destination.resolve() == source.resolve():
      return destination
    if destination.exists():
      stem = destination.stem
      suffix = destination.suffix
      count = 2
      while destination.exists():
        destination = destination_dir / f"{stem}_{count:02d}{suffix}"
        count += 1
    shutil.copy2(source, destination)
    return destination


def organise_export(data: dict[str, Any], videos: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any] | None:
    if not args.export_dir:
      return None

    export_root = Path(args.export_dir).expanduser()
    set_name = safe_name(args.set_name)
    set_root = export_root / "VIDZ_EXPORT" / "sets" / set_name
    media_root = set_root / "media"
    thumbs_root = set_root / "thumbnails"
    index_root = export_root / "VIDZ_EXPORT" / "indexes"
    log_root = export_root / "VIDZ_EXPORT" / "logs"

    set_root.mkdir(parents=True, exist_ok=True)
    index_root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)

    exported = deepcopy(data)
    exported_videos: list[dict[str, Any]] = []
    copied_media = 0
    copied_thumbs = 0
    missing_media: list[str] = []

    for item in videos:
      next_item = deepcopy(item)
      source_path = Path(str(item.get("path") or ""))
      group = group_for(item, args.organise_by)

      if args.copy_media:
        copied = copy_unique(source_path, media_root / group)
        if copied:
          copied_media += 1
          relative = copied.relative_to(set_root)
          next_item["path"] = str(copied)
          next_item["url"] = file_url(args.player_url, relative)
          next_item["exportGroup"] = group
        else:
          missing_media.append(str(source_path))

      thumb_path = Path(str(item.get("thumbnail") or ""))
      if args.copy_thumbs and thumb_path.exists():
        copied_thumb = copy_unique(thumb_path, thumbs_root / group)
        if copied_thumb:
          copied_thumbs += 1
          next_item["thumbnail"] = copied_thumb.relative_to(set_root).as_posix()

      exported_videos.append(next_item)

    exported["videos"] = exported_videos
    exported["export"] = {
      "setName": set_name,
      "exportedAt": datetime.now(timezone.utc).isoformat(),
      "exportRoot": str(export_root),
      "setRoot": str(set_root),
      "organiseBy": args.organise_by,
      "copyMedia": args.copy_media,
      "copyThumbs": args.copy_thumbs,
      "copiedMedia": copied_media,
      "copiedThumbs": copied_thumbs,
      "missingMedia": missing_media,
    }

    set_index = set_root / "media-index.json"
    archive_index = index_root / f"{set_name}.json"
    set_index.write_text(json.dumps(exported, indent=2), encoding="utf-8")
    archive_index.write_text(json.dumps(exported, indent=2), encoding="utf-8")
    (log_root / f"{set_name}.log").write_text(
      f"FILTR OK\nvideos={len(videos)}\ncopied_media={copied_media}\ncopied_thumbs={copied_thumbs}\n",
      encoding="utf-8",
    )
    return exported["export"]


def filter_data(data: dict[str, Any], args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    output = deepcopy(data)
    videos = [item for item in data.get("videos", []) if keep(item, args)]
    videos.sort(key=sort_key(args.sort), reverse=args.reverse)
    if args.limit > 0:
      videos = videos[: args.limit]
    output["videos"] = videos
    output["filtr"] = {
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
      "source": str(args.input),
      "setName": args.set_name,
    }
    return output, videos


def main() -> int:
    args = parse_args()
    source = Path(args.input)
    data = json.loads(source.read_text(encoding="utf-8"))
    output, videos = filter_data(data, args)
    export = organise_export(data, videos, args)
    if export:
      output["export"] = export
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"FILTR OK: {len(videos)}/{len(data.get('videos', []))} videos -> {args.output}")
    if export:
      print(f"EXPORT OK: {export['setRoot']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
