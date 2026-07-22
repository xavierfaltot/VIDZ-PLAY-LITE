#!/usr/bin/env python3
"""Build a lightweight media index for VIDZ PLAY LITE.

The scanner is made for kiosk/Raspberry Pi use: point it at a video SD card
and an optional audio SD card, then serve index.html next to media-index.json.
It stores references and cached metadata only. It does not copy large media.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import mimetypes
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote


VIDEO_EXTS = {".mp4", ".m4v", ".mov", ".webm", ".mkv", ".avi"}
AUDIO_EXTS = {".mp3", ".wav", ".aiff", ".aif", ".flac", ".m4a", ".aac", ".ogg"}
ANALYSIS_VERSION = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan media cards for VIDZ PLAY LITE.")
    parser.add_argument("--video", required=True, help="Video folder or mounted SD card path.")
    parser.add_argument("--audio", help="Audio folder or mounted SD card path.")
    parser.add_argument("--output", default="media-index.json", help="Output JSON index path.")
    parser.add_argument("--cache", default="cache", help="Cache folder for generated thumbnails.")
    parser.add_argument("--video-url", default="", help="URL prefix used by the local web server for videos.")
    parser.add_argument("--audio-url", default="", help="URL prefix used by the local web server for audio.")
    parser.add_argument("--cut-step", type=float, default=0.5, help="Seconds between sampled frames for cut detection.")
    parser.add_argument("--cut-threshold", type=float, default=0.18, help="Mean frame difference threshold for cuts.")
    parser.add_argument("--max-cut-samples", type=int, default=480, help="Maximum frames sampled per video.")
    return parser.parse_args()


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def run_json(command: list[str]) -> dict[str, Any] | None:
    try:
      result = subprocess.run(command, check=True, capture_output=True, text=True)
      return json.loads(result.stdout or "{}")
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
      return None


def run_bytes(command: list[str]) -> bytes:
    try:
      result = subprocess.run(command, check=True, capture_output=True)
      return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
      return b""


def list_media(root: Path, exts: set[str]) -> list[Path]:
    if not root.exists():
      return []
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in exts)


def media_id(path: Path) -> str:
    stat = path.stat()
    raw = f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def url_for(path: Path, root: Path, prefix: str) -> str:
    try:
      rel = path.relative_to(root).as_posix()
    except ValueError:
      rel = path.name
    encoded = quote(rel)
    if not prefix:
      return encoded
    return f"{prefix.rstrip('/')}/{encoded}"


def probe(path: Path) -> dict[str, Any] | None:
    return run_json([
      "ffprobe",
      "-v",
      "error",
      "-print_format",
      "json",
      "-show_format",
      "-show_streams",
      str(path),
    ])


def stream_of(data: dict[str, Any] | None, kind: str) -> dict[str, Any]:
    if not data:
      return {}
    for stream in data.get("streams", []):
      if stream.get("codec_type") == kind:
        return stream
    return {}


def duration_of(data: dict[str, Any] | None) -> float:
    if not data:
      return 0.0
    value = data.get("format", {}).get("duration")
    try:
      return max(0.0, float(value))
    except (TypeError, ValueError):
      return 0.0


def fps_of(stream: dict[str, Any]) -> float:
    raw = stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "0/1"
    try:
      num, den = raw.split("/")
      den_value = float(den)
      return float(num) / den_value if den_value else 0.0
    except (ValueError, ZeroDivisionError):
      return 0.0


def orientation(width: int, height: int) -> str:
    if not width or not height:
      return ""
    ratio = width / height
    if ratio > 1.2:
      return "wide"
    if ratio < 0.82:
      return "vertical"
    return "square"


def thumbnail(path: Path, output: Path, duration: float) -> str:
    output.parent.mkdir(parents=True, exist_ok=True)
    seek = max(0.1, duration * 0.1) if duration else 0.1
    command = [
      "ffmpeg",
      "-y",
      "-v",
      "error",
      "-ss",
      f"{seek:.3f}",
      "-i",
      str(path),
      "-frames:v",
      "1",
      "-vf",
      "scale=360:-1",
      str(output),
    ]
    try:
      subprocess.run(command, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
      return ""
    return output.as_posix()


def rgb_frame(path: Path, time: float, width: int = 96, height: int = 54) -> bytes:
    return run_bytes([
      "ffmpeg",
      "-v",
      "error",
      "-ss",
      f"{max(0, time):.3f}",
      "-i",
      str(path),
      "-frames:v",
      "1",
      "-vf",
      f"scale={width}:{height}",
      "-f",
      "rawvideo",
      "-pix_fmt",
      "rgb24",
      "pipe:1",
    ])


def frame_stats(frame: bytes) -> dict[str, float | str]:
    if not frame:
      return {"brightness": 0.0, "contrast": 0.0, "dominantColor": "#000000"}
    pixels = len(frame) // 3
    lumas: list[float] = []
    red = green = blue = 0
    for i in range(0, len(frame), 3):
      r, g, b = frame[i], frame[i + 1], frame[i + 2]
      red += r
      green += g
      blue += b
      lumas.append((0.2126 * r + 0.7152 * g + 0.0722 * b) / 255)
    avg = sum(lumas) / max(1, pixels)
    variance = sum((value - avg) ** 2 for value in lumas) / max(1, pixels)
    color = f"#{round(red / pixels):02x}{round(green / pixels):02x}{round(blue / pixels):02x}"
    return {"brightness": avg, "contrast": math.sqrt(variance), "dominantColor": color}


def frame_diff(a: bytes, b: bytes) -> float:
    if not a or not b or len(a) != len(b):
      return 0.0
    stride = 9
    total = 0
    count = 0
    for i in range(0, len(a), stride):
      total += abs(a[i] - b[i]) + abs(a[i + 1] - b[i + 1]) + abs(a[i + 2] - b[i + 2])
      count += 3
    return total / max(1, count) / 255


def label_brightness(value: float) -> str:
    if value < 0.38:
      return "dark"
    if value > 0.64:
      return "bright"
    return "mid"


def label_motion(value: float) -> str:
    if value < 0.07:
      return "slow"
    if value > 0.16:
      return "fast"
    return "medium"


def label_energy(score: float) -> str:
    if score >= 0.14:
      return "high"
    if score >= 0.075:
      return "medium"
    return "low"


def analyse_video(path: Path, duration: float, step: float, threshold: float, max_samples: int) -> dict[str, Any]:
    sample_times = [0.1]
    if duration:
      sample_times = sorted({max(0.1, duration * pct) for pct in (0.1, 0.45, 0.75)})
    frames = [rgb_frame(path, time) for time in sample_times]
    frames = [frame for frame in frames if frame]
    base_stats = frame_stats(frames[0] if frames else b"")
    motion = 0.0
    if len(frames) > 1:
      diffs = [frame_diff(frames[i - 1], frames[i]) for i in range(1, len(frames))]
      motion = sum(diffs) / len(diffs)
    brightness = float(base_stats["brightness"])
    contrast = float(base_stats["contrast"])
    energy_score = motion * 0.5 + contrast * 0.3 + abs(brightness - 0.5) * 0.2

    cuts = [{"time": 0.0, "type": "start", "confidence": 1.0}]
    previous = None
    samples = 0
    if duration > step and max_samples > 0:
      time = step
      while time < duration and samples < max_samples:
        current = rgb_frame(path, time, 64, 36)
        if previous:
          diff = frame_diff(previous, current)
          if diff >= threshold:
            cuts.append({"time": round(time, 3), "type": "cut", "confidence": min(1.0, round(diff / threshold, 3))})
        previous = current
        time += step
        samples += 1

    return {
      "brightness": label_brightness(brightness),
      "brightnessValue": round(brightness, 4),
      "contrast": round(contrast, 4),
      "motion": label_motion(motion),
      "motionValue": round(motion, 4),
      "dominantColor": base_stats["dominantColor"],
      "energy": label_energy(energy_score),
      "energyScore": round(energy_score, 4),
      "cuts": cuts,
      "cutCount": max(0, len(cuts) - 1),
    }


def tags_for(item: dict[str, Any]) -> list[str]:
    tags = {
      item.get("orientation", ""),
      item.get("brightness", ""),
      item.get("motion", ""),
      item.get("energy", ""),
    }
    duration = float(item.get("duration") or 0)
    if duration and duration < 30:
      tags.add("short")
    elif duration >= 180:
      tags.add("long")
    else:
      tags.add("medium")
    return sorted(tag for tag in tags if tag)


def video_entry(path: Path, root: Path, cache: Path, video_url: str, args: argparse.Namespace, has_ffmpeg: bool) -> dict[str, Any]:
    data = probe(path) if command_exists("ffprobe") else None
    stream = stream_of(data, "video")
    duration = duration_of(data)
    width = int(stream.get("width") or 0)
    height = int(stream.get("height") or 0)
    item_id = media_id(path)
    thumb = ""
    analysis: dict[str, Any] = {
      "brightness": "",
      "motion": "",
      "dominantColor": "#000000",
      "energy": "",
      "cuts": [{"time": 0.0, "type": "start", "confidence": 1.0}],
      "cutCount": 0,
    }
    if has_ffmpeg:
      thumb = thumbnail(path, cache / "thumbs" / f"{item_id}.jpg", duration)
      analysis = analyse_video(path, duration, args.cut_step, args.cut_threshold, args.max_cut_samples)
    item = {
      "id": item_id,
      "name": path.name,
      "folder": path.parent.relative_to(root).as_posix() if path.parent != root else "",
      "path": str(path),
      "url": url_for(path, root, video_url),
      "type": mimetypes.guess_type(path.name)[0] or "video/mp4",
      "duration": round(duration, 3),
      "width": width,
      "height": height,
      "fps": round(fps_of(stream), 3),
      "orientation": orientation(width, height),
      "thumbnail": thumb,
      "analysisVersion": ANALYSIS_VERSION,
      **analysis,
    }
    item["tags"] = tags_for(item)
    return item


def audio_entry(path: Path, root: Path, audio_url: str) -> dict[str, Any]:
    data = probe(path) if command_exists("ffprobe") else None
    return {
      "id": media_id(path),
      "name": path.name,
      "folder": path.parent.relative_to(root).as_posix() if path.parent != root else "",
      "path": str(path),
      "url": url_for(path, root, audio_url),
      "type": mimetypes.guess_type(path.name)[0] or "audio/mpeg",
      "duration": round(duration_of(data), 3),
    }


def main() -> int:
    args = parse_args()
    video_root = Path(args.video).expanduser().resolve()
    audio_root = Path(args.audio).expanduser().resolve() if args.audio else None
    output = Path(args.output).expanduser()
    cache = Path(args.cache).expanduser()
    has_ffmpeg = command_exists("ffmpeg")

    videos = [
      video_entry(path, video_root, cache, args.video_url, args, has_ffmpeg)
      for path in list_media(video_root, VIDEO_EXTS)
    ]
    audio = [
      audio_entry(path, audio_root, args.audio_url)
      for path in (list_media(audio_root, AUDIO_EXTS) if audio_root else [])
    ]

    index = {
      "project": "VIDZ PLAY LITE",
      "version": 1,
      "generatedAt": datetime.now(timezone.utc).isoformat(),
      "videoRoot": str(video_root),
      "audioRoot": str(audio_root) if audio_root else "",
      "videos": videos,
      "audio": audio,
    }
    output.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"SCAN OK: {len(videos)} videos, {len(audio)} audio files -> {output}")
    if not has_ffmpeg:
      print("WARNING: ffmpeg not found. Index created without thumbnails/cuts/analysis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
