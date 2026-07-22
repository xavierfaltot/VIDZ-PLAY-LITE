# VIDZ PLAY LITE Blocks

VIDZ PLAY LITE is organised as chainable blocks for machine use.

```text
SCAN -> FILTER -> PLAY
```

Each block has one job and passes a simple file contract to the next block.

## 01 / SCAN

Input:

```text
Video SD card
Audio SD card, optional
```

Output:

```text
media-index.json
cache/thumbs/
```

Command:

```bash
python3 tools/vidz_scan_lite.py \
  --video /media/VIDZ_VIDEO \
  --audio /media/VIDZ_AUDIO \
  --output media-index.json \
  --cache cache \
  --video-url /media/video \
  --audio-url /media/audio
```

Purpose:

- find media files
- read duration and resolution
- generate thumbnails
- detect cuts
- estimate brightness, motion and energy
- write a machine-readable media index

## 02 / FILTER

Input:

```text
media-index.json
```

Output:

```text
media-index.filtered.json
```

Command examples:

```bash
python3 tools/vidz_filter_lite.py --input media-index.json --output media-index.filtered.json --energy high
```

```bash
python3 tools/vidz_filter_lite.py --input media-index.json --output media-index.filtered.json --motion fast --orientation wide --sort energy --reverse
```

Purpose:

- keep only the clips needed for the current set
- filter by energy, motion, brightness, orientation, tag, folder or duration
- sort by name, duration, energy or cuts
- output a new player-ready index

## 03 / PLAY

Input:

```text
media-index.json
```

or:

```text
media-index.filtered.json renamed/copied to media-index.json
```

Output:

```text
HDMI fullscreen playback
Optional audio output
```

Purpose:

- load prepared media automatically
- filter live with the on-screen FILTER controls
- play local video sources with the Lite engine

## Chain Contract

Every block passes JSON with this minimum shape:

```json
{
  "project": "VIDZ PLAY LITE",
  "version": 1,
  "videos": [],
  "audio": []
}
```

The player only needs `videos[].url`, `videos[].name` and optional metadata. Extra analysis stays useful but is not required.
