# VIDZ PLAY LITE Box Bill Of Materials

Based on the low-tech multi-screen front panel concept.

Goal:

```text
Raspberry Pi video box
multiple small status screens
physical buttons
VIDEO CARD / AUDIO CARD / EXPORT CARD
MIC fallback
LINE IN direct audio
HDMI OUT
```

## V1 Shopping List

### 01 / Core Computer

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | Raspberry Pi 5, 8GB | Recommended for Chromium kiosk, video playback and scanning. 4GB can work, 8GB gives more margin. |
| 1 | Official Raspberry Pi 27W USB-C Power Supply | Required for Pi 5 with USB peripherals. |
| 1 | Official Raspberry Pi 5 Active Cooler | Required for long scanning/playback sessions in a closed box. |
| 1 | 64GB or 128GB high-endurance microSD | System card only. Media cards stay removable. |
| 1 | Short micro-HDMI to HDMI cable or panel mount adapter | Main video output. |

### 02 / Small Screens

Recommended V1: small monochrome OLEDs, not touchscreens.

| Qty | Part | Notes |
| --- | --- | --- |
| 3 | 2.42 inch OLED 128x64 I2C/SPI, SSD1309 | For `SCAN`, `FILTR`, `PLAY`. |
| 1 | 0.96 inch or 1.3 inch OLED I2C | For small global `STATUS` or `AUDIO`. Optional if the 3 main screens are enough. |
| 1 | TCA9548A I2C multiplexer | Needed when several identical I2C screens share the same address. |
| 1 | GPIO ribbon cable + breakout / terminal block | Makes wiring clean and serviceable. |

Screen labels:

```text
01 / SCAN
02 / FILTR
03 / PLAY
STATUS / AUDIO
```

### 03 / Buttons And LEDs

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | Large green momentary arcade button | `SCAN`. |
| 1 | Large violet/purple momentary arcade button | `FILTR`. |
| 1 | Large amber/orange momentary arcade button | `PLAY`. |
| 1 | Red momentary arcade button | `STOP` or `BLACK`. |
| 6-10 | 12mm LED indicators, 5V or 3.3V compatible | Card/status LEDs. |
| 10-20 | Resistors for LEDs | Use values matching LED voltage/current. |
| 1 | MCP23017 I/O expander board | Recommended if GPIO gets crowded. |
| 1 | Emergency-style toggle or guarded switch, optional | For `BLACK` or safe shutdown. |

LED labels:

```text
VIDEO CARD
AUDIO CARD
EXPORT CARD
HDMI OUT
AUDIO OUT
FILE
MIC
LINE IN
READY
ERROR
```

### 04 / Card Slots

Because Raspberry Pi has one native microSD slot, use USB card readers for removable media.

| Qty | Part | Notes |
| --- | --- | --- |
| 3 | USB SD/microSD card readers | `VIDEO CARD`, `AUDIO CARD`, `EXPORT CARD`. |
| 1 | Powered USB 3 hub, compact | Strongly recommended if using 3 card readers + audio interface + mic. |
| 3 | Panel mount USB-A or USB-C extensions | Lets cards/readers appear cleanly on the front/side of the box. |

Recommended card roles:

```text
VIDEO CARD  = source clips
AUDIO CARD  = music/audio files
EXPORT CARD = sorted sets/indexes/thumbnails
```

### 05 / Audio

Raspberry Pi does not provide a proper direct analogue line input. Use an audio interface.

Recommended simple route:

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | Class-compliant USB audio interface with stereo line input | For `LINE IN`. |
| 1 | Behringer UCA202 or similar | Cheap stereo RCA line input/output option. |
| 1 | Small USB microphone or USB mic module | Built-in fallback `MIC`. |
| 1 | 3.5mm/TRS/RCA panel mount jacks | Depends on chosen audio interface. |
| 1 | Ground-loop isolator, optional | Useful if connected to mixers/projectors. |

Better but more expensive route:

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | 2-in/2-out class-compliant USB audio interface | Example type: Focusrite/Behringer/Arturia style. Gives cleaner line/mic input. |

Avoid for V1:

```text
Bluetooth as the main live audio path
AirPlay as tight beat-critical input
cheap mono USB sound dongles for stereo line-in
```

### 06 / Enclosure And Mechanics

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | Metal or ABS project enclosure, approx 300-400mm wide | Big enough for Pi, screens, readers, audio and buttons. |
| 1 | 2-3mm aluminium front panel | Easier to drill/cut and gives the hardware feel. |
| 1 | Standoffs, M2.5/M3 screws, washers | Mount Pi, boards and screens. |
| 1 | Vent grille or slots | Needed for cooling. |
| 1 | Small 5V case fan, optional | Useful if enclosure is tight. |
| 1 | Cable glands / strain relief | For HDMI, power, audio. |
| 1 | Label plates or engraved labels | Front-panel typography. |

### 07 / Cables And Wiring

| Qty | Part | Notes |
| --- | --- | --- |
| 1 | Dupont jumper wire kit | Prototype wiring. |
| 1 | JST/XH connector kit | Cleaner final wiring. |
| 1 | Heat-shrink tubing kit | Protect joins. |
| 1 | Ferrite cores, optional | Useful for noisy USB/audio builds. |
| 1 | USB-C panel mount extension | Power input. |
| 1 | HDMI panel mount extension | Video output. |

## Minimum Working Prototype

Buy this first:

```text
Raspberry Pi 5 8GB
Official 27W USB-C power supply
Official Active Cooler
128GB system microSD
3 x USB SD/microSD card readers
powered USB hub
1 x USB audio interface with stereo line input
1 x USB microphone
3 x large arcade buttons
3 x 2.42 inch OLED screens
1 x TCA9548A I2C multiplexer
project enclosure
HDMI cable
```

This is enough to test:

```text
VIDEO CARD inserted
AUDIO CARD inserted
EXPORT CARD inserted
press SCAN
press FILTR
press PLAY
HDMI output works
audio input from FILE / MIC / LINE IN
```

## Recommended V1 Architecture

```text
Raspberry Pi 5
├── HDMI OUT -> projector / monitor
├── USB hub
│   ├── VIDEO CARD reader
│   ├── AUDIO CARD reader
│   ├── EXPORT CARD reader
│   ├── USB audio interface LINE IN/OUT
│   └── USB mic
├── GPIO
│   ├── arcade buttons
│   ├── status LEDs
│   ├── TCA9548A I2C multiplexer
│   └── OLED screens
└── system microSD
```

## Do Not Buy Yet

For the first prototype, do not buy:

```text
custom PCB
custom CNC case
large touchscreen
battery system
Bluetooth audio transmitter as main output
AirPlay receiver hardware
expensive audio interface
```

Build the working box first. Then make the enclosure beautiful.
