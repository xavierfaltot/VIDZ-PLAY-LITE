# VIDZ PLAY LITE Low-Tech Multi-Screen Interface Prompt

Design a physical Raspberry Pi video instrument interface for VIDZ PLAY LITE.

This must not feel like an iPad app.
This must not feel like a web dashboard.
This must feel like a low-key, low-tech hardware box with several small screens.

## Core Idea

VIDZ PLAY LITE is a small video machine.

The Raspberry Pi is hidden inside the box.
The interface is split across multiple small displays and physical controls.

Main chain:

```text
SCAN -> FILTR -> PLAY
```

On-screen labels must be in English.

## Physical Display Layout

Use several small screens instead of one big tablet screen.

Recommended display zones:

```text
┌─────────────────────────────────────────────────────────┐
│ [STATUS OLED] [SCAN OLED] [FILTR OLED] [AUDIO OLED]     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                 MAIN VIDEO HDMI SCREEN                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ [VIDEO CARD] [AUDIO CARD] [EXPORT CARD] [LINE IN]       │
│ [SCAN]       [FILTR]      [PLAY]        [STOP]          │
└─────────────────────────────────────────────────────────┘
```

## Screens

### 01 / STATUS OLED

Small monochrome or low-colour display.

Shows:

```text
VIDZ PLAY LITE
READY
HDMI OUT
CPU 42%
TEMP OK
```

### 02 / SCAN OLED

Shows scan progress only.

```text
SCAN
VIDEO CARD OK
AUDIO CARD OK
124 CLIPS
INDEX READY
```

### 03 / FILTR OLED

Shows organisation/filter state.

```text
FILTR
ENERGY HIGH
SORT CUTS
SET READY
EXPORT OK
```

### 04 / AUDIO OLED

Shows audio source.

```text
AUDIO
FILE
MIC OFF
LINE IN ON
LEVEL 74%
```

### 05 / MAIN VIDEO SCREEN

This is not a control dashboard.
It is the video output monitor.

It shows:

```text
MASTER VIDEO
or fullscreen HDMI output
```

No menus should cover this screen during performance.

## Physical Controls

Use real buttons and simple controls.

Suggested front panel:

```text
[SCAN] [FILTR] [PLAY] [STOP]

[VIDEO CARD] [AUDIO CARD] [EXPORT CARD]

[FILE] [MIC] [LINE IN]

[PREV] [NEXT] [RANDOM]

[CUT] [AUTO] [BLACK]

MASTER KNOB
SENSITIVITY KNOB
```

## Button Behaviour

### SCAN

Runs:

```text
vidz_scan_lite.py
```

Output:

```text
media-index.json
cache/thumbs/
```

### FILTR

Runs:

```text
vidz_filtr_lite.py
```

Does:

- filter clips
- sort clips
- organise export card
- write set index
- optionally copy selected media

### PLAY

Launches:

```text
index.html
```

In kiosk fullscreen mode.

### BLACK

Cuts video output to black.

### AUTO

Starts automatic clip switching.

## Visual Style

Low-tech.
Functional.
Not shiny.
Not futuristic.

References:

- field recorder
- old video switcher
- sampler rack
- lab equipment
- DIY broadcast box

Avoid:

- iPad app look
- SaaS dashboard
- glossy touchscreen UI
- complex menus
- big gradients
- decorative UI

Use:

- black graphite
- dull metal
- small monochrome screens
- amber/green status text
- physical buttons
- engraved labels
- simple LEDs
- chunky typography

## Colour Code

```text
SCAN  = green
FILTR = violet
PLAY  = amber/orange
REC   = red
READY = green
ERROR = red
```

## Interaction Rule

The user should not operate this like a computer.

The user should operate it like hardware:

```text
insert cards
press SCAN
press FILTR
press PLAY
```

## Final Design Sentence

VIDZ PLAY LITE is not a tablet interface.
It is a small Raspberry Pi video instrument with several simple screens, physical controls, and a low-key broadcast-machine attitude.
