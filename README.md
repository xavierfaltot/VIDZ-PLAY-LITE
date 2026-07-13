# VIDZ PLAY LITE

VIDZ PLAY LITE is the lightweight version of VIDZ PLAY: a single-file browser instrument for playing local video folders with automatic live mixing.

Repository: https://github.com/xavierfaltot/VIDZ-PLAY-LITE

This repository contains only the Lite version. It is made for fast setup, local playback, and a direct performance flow. Load a folder of videos, optionally load an audio file or use microphone input, then press play. The engine alternates clips, reacts to timing, applies visual blend/effect logic, and runs fully in the browser.

No server. No cloud upload. No bundled media.

The full version is available on demand.

## Features

- Local video folder import
- Optional local audio file
- Optional microphone-reactive mode
- Fullscreen video stage
- Two hidden video decks for continuous playback
- Automatic clip switching
- Smart visual mixing and FX
- Scene/energy-aware timing logic
- Local-only playback through the browser
- Mobile/touch-oriented interface

## Run

Open:

```text
index.html
```

Then:

1. Press `ADD VIDEO(S)`.
2. Select video files or a video folder.
3. Optionally add an audio file.
4. Press the central play control.

For best results, use Chrome or another Chromium browser because folder import uses browser file APIs.

## GitHub Pages

This repository is ready for GitHub Pages.

Use:

```text
Settings -> Pages -> Deploy from branch -> main -> /root
```

The public entry point is:

```text
index.html
```

## Files

```text
index.html
assets/vidz-play-lite-logo.png
README.md
LICENSE
.gitignore
```

## Privacy

VIDZ PLAY LITE reads local files through the browser file picker. Videos and audio are not uploaded by the app.

Microphone input, when enabled, is used locally for reactive playback only.

## Notes

This is a live-playback instrument, not an editing timeline. It is designed for quick visual sets, tests, demos, and lightweight performance situations where opening a folder and playing immediately matters more than building a full project.

The full version of VIDZ PLAY is available on demand for expanded controls and dedicated performance setups.
