# VIDZ PLAY LITE Raspberry Pi Box

This document describes the physical box layout for a standalone VIDZ PLAY LITE machine.

## I/O Layout

```text
VIDEO CARD  -> scan video files
AUDIO CARD  -> scan audio files
EXPORT CARD -> receive sorted/exported files and generated indexes
MIC          -> built-in fallback audio input
LINE IN      -> direct external audio input
HDMI OUT     -> video output
AUDIO OUT    -> local sound output
BLUETOOTH    -> optional wireless audio output
AIRPLAY      -> optional network audio input
```

## Interface Direction

Do not design the box as an iPad-style touchscreen.

Design it as a low-tech hardware instrument with multiple small screens:

```text
STATUS OLED
SCAN OLED
FILTR OLED
AUDIO OLED
MAIN HDMI VIDEO
```

Detailed interface prompt:

```text
interface/low-tech-multi-screen-prompt.md
```

Bill of materials:

```text
hardware/bill-of-materials.md
```

Assembly guide:

```text
hardware/assembly-guide.md
```

## Storage

The Raspberry Pi boots from its own system storage. The performance media should be removable.

Recommended removable slots:

```text
Slot 1 / VIDEO CARD
Slot 2 / AUDIO CARD
Slot 3 / EXPORT CARD
```

Because a standard Raspberry Pi has only one native microSD slot, use USB card readers for the removable media slots.

## Export Card

The export card is used by the organiser block.

It can receive:

- sorted clips
- filtered clip sets
- `media-index.json`
- `media-index.filtr.json`
- thumbnails cache
- logs
- set presets

Suggested structure:

```text
EXPORT CARD/
  VIDZ_EXPORT/
    indexes/
    thumbnails/
    sets/
    logs/
```

The export card should not be required for playback. If it is missing, VIDZ PLAY LITE can still scan and play.

## Built-In Microphone

A built-in microphone can be used as fallback when no audio card or line input is connected.

Use case:

```text
No audio file loaded -> use MIC as rhythm/energy input
```

The mic should be treated as control audio, not as final high-quality programme audio.

In the browser player, this uses:

```text
navigator.mediaDevices.getUserMedia()
```

## Direct Audio Input

Yes, the box can have a direct audio input.

Best approach:

```text
External source -> USB audio interface or audio HAT -> Raspberry Pi -> Web Audio API
```

Supported inputs:

- line input from mixer
- DJ booth output
- synth/drum machine output
- phone/player output
- microphone input, if the interface has mic preamp

Important:

```text
LINE IN and MIC IN are not the same level.
```

For a reliable live box, use a class-compliant USB audio interface with stereo line input. The browser can then use it as an audio input device.

## Audio Mixing

The player can be extended so audio sources become selectable:

```text
AUDIO SOURCE
[FILE] [MIC] [LINE IN] [AIRPLAY]
```

Recommended behaviour:

- `FILE`: play audio from the audio card or imported file
- `MIC`: listen to built-in mic for reactive cuts
- `LINE IN`: use direct audio input for reactive cuts and optional monitoring
- `AIRPLAY`: receive network audio and use it as source

For the Lite version, the first priority is analysis/reactivity. Programme audio output can stay pass-through from the external mixer if needed.

## HDMI Output

HDMI is the main visual output.

Recommended mode:

```text
Chromium kiosk -> fullscreen canvas -> HDMI OUT
```

## Bluetooth

Bluetooth audio output is possible, but it can add latency.

Recommended use:

- setup monitoring
- small speakers
- non-critical playback

For live performance, wired audio output is safer.

## AirPlay

AirPlay can be added as a separate receiver service on the Raspberry Pi.

Recommended role:

```text
AIRPLAY IN -> audio source for analysis/reactivity
```

Avoid relying on AirPlay for tight beat-accurate live performance because network latency can vary.

## Block Chain

The physical box can use this chain:

```text
MOUNT CARDS
-> SCAN
-> FILTR / ORGANISE / EXPORT
-> PLAY
```

Next block to build:

```text
FILTR / ORGANISE / EXPORT
```

Purpose:

- read `media-index.json`
- filter and create organised folders or set files
- copy lightweight indexes to the export card
- optionally copy selected media to the export card when requested

## Display Labels

Use English labels on the physical machine:

```text
VIDEO CARD
AUDIO CARD
EXPORT CARD
MIC
LINE IN
HDMI OUT
AUDIO OUT
AIRPLAY
BLUETOOTH
```
