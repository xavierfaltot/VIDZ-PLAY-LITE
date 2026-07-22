# VIDZ PLAY LITE Box Assembly Guide

Guide de fabrication façon IKEA / LEGO.

Objectif:

```text
un boîtier Raspberry Pi low-tech
avec plusieurs petits écrans
des boutons physiques
3 cartes médias
une sortie HDMI
une entrée audio directe
un micro de secours
```

Les labels visibles sur la machine restent en anglais.

## Avant De Commencer

### Pièces principales

```text
[A] Raspberry Pi 5
[B] Official 27W USB-C power supply
[C] Active Cooler
[D] System microSD
[E] Powered USB hub
[F] 3 x USB card readers
[G] 3 x OLED screens
[H] TCA9548A I2C multiplexer
[I] Arcade buttons: SCAN / FILTR / PLAY / BLACK
[J] Status LEDs
[K] USB audio interface
[L] USB microphone
[M] HDMI panel mount
[N] USB-C power panel mount
[O] enclosure + front panel
```

### Outils

```text
small screwdriver
drill
step drill bit
small files
wire cutter
wire stripper
multimeter
label printer or engraved labels
hot glue or double-sided foam tape for prototype only
```

### Règle De Sécurité

```text
Do not wire or rewire while powered.
Check polarity before connecting LEDs.
Keep metal enclosure away from exposed 5V/GPIO contacts.
Use standoffs under every board.
```

## Vue Finale

```text
┌────────────────────────────────────────────────────────────┐
│  01 / SCAN       02 / FILTR       03 / PLAY      STATUS    │
│  [ OLED ]        [ OLED ]         [ OLED ]       [ LEDs ]  │
│                                                            │
│       [ SCAN ]       [ FILTR ]       [ PLAY ]              │
│                                                            │
│ VIDEO CARD   AUDIO CARD   EXPORT CARD   MIC   LINE IN      │
│ HDMI OUT     AUDIO OUT     POWER                           │
└────────────────────────────────────────────────────────────┘
```

## Phase 1 / Préparer Le Cerveau

### Step 1

Prends:

```text
[A] Raspberry Pi 5
[C] Active Cooler
```

Action:

```text
clipser l'Active Cooler sur le Raspberry Pi
ne pas encore enfermer le Pi dans le boîtier
```

Test:

```text
le cooler est bien plaqué
le ventilateur peut tourner librement
```

### Step 2

Prends:

```text
[D] system microSD
```

Action:

```text
installer Raspberry Pi OS
activer SSH si besoin
installer Chromium
installer ffmpeg
copier le repo VIDZ-PLAY-LITE
```

Commande:

```bash
sudo apt update
sudo apt install -y chromium-browser ffmpeg python3
```

Test:

```text
le Pi démarre
Chromium s'ouvre
ffmpeg répond dans le terminal
```

## Phase 2 / Préparer Les Cartes

### Step 3

Prends:

```text
[E] powered USB hub
[F] 3 x USB card readers
```

Action:

```text
brancher les 3 lecteurs de cartes dans le hub
brancher le hub au Raspberry Pi
```

Labels:

```text
reader 1 = VIDEO CARD
reader 2 = AUDIO CARD
reader 3 = EXPORT CARD
```

Test:

```bash
lsblk
```

Tu dois voir les cartes apparaître comme périphériques séparés.

### Step 4

Prépare trois cartes:

```text
VIDEO CARD
  /clips

AUDIO CARD
  /audio

EXPORT CARD
  /VIDZ_EXPORT
```

Test:

```text
mettre 2 ou 3 vidéos dans VIDEO CARD
mettre 1 audio dans AUDIO CARD
laisser EXPORT CARD vide
```

## Phase 3 / Faire Fonctionner SCAN Et FILTR Sans Boîtier

### Step 5

Action:

```text
scanner les cartes avant tout câblage compliqué
```

Exemple:

```bash
python3 tools/vidz_scan_lite.py \
  --video /media/VIDZ_VIDEO \
  --audio /media/VIDZ_AUDIO \
  --output media-index.json \
  --cache cache \
  --video-url /media/video \
  --audio-url /media/audio
```

Résultat attendu:

```text
SCAN OK
media-index.json créé
cache/thumbs créé
```

### Step 6

Action:

```text
organiser/exporter avec FILTR
```

Exemple:

```bash
python3 tools/vidz_filtr_lite.py \
  --input media-index.json \
  --set-name TEST_SET \
  --export-dir /media/VIDZ_EXPORT_CARD \
  --copy-thumbs \
  --organise-by energy
```

Résultat attendu:

```text
FILTR OK
EXPORT OK
VIDZ_EXPORT/sets/TEST_SET créé
```

Ne continue pas le montage physique tant que `SCAN` et `FILTR` ne répondent pas.

## Phase 4 / Écrans OLED

### Step 7

Prends:

```text
[G] 3 x OLED screens
[H] TCA9548A I2C multiplexer
```

Pourquoi:

```text
plusieurs OLED identiques ont souvent la même adresse I2C
le TCA9548A permet de les séparer en canaux
```

### Step 8

Connexion générale:

```text
Raspberry Pi GPIO 3.3V  -> TCA9548A VIN
Raspberry Pi GND       -> TCA9548A GND
Raspberry Pi SDA       -> TCA9548A SDA
Raspberry Pi SCL       -> TCA9548A SCL

TCA channel 0 -> OLED SCAN
TCA channel 1 -> OLED FILTR
TCA channel 2 -> OLED PLAY
TCA channel 3 -> OLED STATUS, optional
```

Test:

```bash
i2cdetect -y 1
```

Résultat attendu:

```text
adresse du TCA visible, souvent 0x70
```

### Step 9

Pose les écrans en façade:

```text
gauche  = 01 / SCAN
centre  = 02 / FILTR
droite  = 03 / PLAY
petit côté = STATUS / AUDIO
```

Conseil:

```text
fixer provisoirement avec ruban mousse
tester
puis seulement après faire les vis définitives
```

## Phase 5 / Boutons

### Step 10

Prends:

```text
[I] arcade buttons
```

Disposition:

```text
[GREEN]  SCAN
[VIOLET] FILTR
[ORANGE] PLAY
[RED]    BLACK / STOP
```

Action:

```text
percer la façade au diamètre des boutons
placer les boutons
serrer les bagues
ne pas forcer sur le plastique
```

### Step 11

Câblage logique:

```text
un côté du bouton -> GPIO
autre côté        -> GND
```

Prévoir:

```text
pull-up interne côté logiciel
```

Exemple de mapping:

```text
GPIO 17 = SCAN
GPIO 27 = FILTR
GPIO 22 = PLAY
GPIO 23 = BLACK / STOP
```

Test simple:

```text
appuyer sur chaque bouton
vérifier dans un petit script Python que l'état change
```

## Phase 6 / LEDs D'état

### Step 12

Prends:

```text
[J] status LEDs
resistors
```

Labels:

```text
VIDEO CARD
AUDIO CARD
EXPORT CARD
HDMI OUT
AUDIO OUT
MIC
LINE IN
READY
ERROR
```

Câblage:

```text
GPIO -> resistor -> LED positive
LED negative -> GND
```

Important:

```text
si LED 5V avec module intégré, vérifier compatibilité GPIO
sinon utiliser transistor/driver
```

Pour V1:

```text
utiliser des LED 3.3V simples avec résistances
ou des modules LED prévus Raspberry Pi
```

## Phase 7 / Audio

### Step 13

Prends:

```text
[K] USB audio interface
[L] USB microphone
```

Branchement:

```text
USB audio interface -> powered USB hub
USB microphone      -> powered USB hub
```

Labels:

```text
FILE
MIC
LINE IN
AUDIO OUT
```

Test:

```bash
arecord -l
aplay -l
```

Résultat attendu:

```text
l'interface audio apparaît comme capture/playback
le micro apparaît comme capture
```

### Step 14

Entrée son directe:

```text
source externe -> LINE IN de l'interface USB
```

Sources possibles:

```text
DJ mixer
phone
synth
drum machine
audio player
```

À éviter:

```text
brancher une sortie amplifiée haut-parleur dans LINE IN
brancher directement un micro passif dans une entrée line sans préampli
```

## Phase 8 / Sorties Et Alimentation

### Step 15

Prends:

```text
[M] HDMI panel mount
[N] USB-C power panel mount
```

Action:

```text
monter HDMI OUT sur la façade arrière ou latérale
monter POWER USB-C
brancher micro-HDMI du Pi vers l'adaptateur panel mount
brancher alimentation vers Pi
```

Test:

```text
image visible sur écran HDMI
pas de coupure quand on bouge légèrement les câbles
```

## Phase 9 / Montage Dans Le Boîtier

### Step 16

Ordre conseillé:

```text
1. fixer le Raspberry Pi sur entretoises
2. fixer le powered USB hub
3. fixer les lecteurs de cartes
4. fixer l'interface audio
5. fixer le TCA9548A
6. fixer les OLED
7. fixer les boutons
8. fixer les LEDs
9. ranger les câbles
10. tester avant fermeture
```

Ne ferme pas le boîtier tant que tout n'a pas été testé.

## Phase 10 / Test Final

### Step 17

Allume la machine.

Tu dois voir:

```text
STATUS OLED -> VIDZ PLAY LITE / READY
SCAN OLED   -> WAITING
FILTR OLED  -> WAITING
PLAY OLED   -> READY
```

### Step 18

Insère:

```text
VIDEO CARD
AUDIO CARD
EXPORT CARD
```

LEDs attendues:

```text
VIDEO CARD = green
AUDIO CARD = green
EXPORT CARD = green
```

### Step 19

Appuie:

```text
SCAN
```

Résultat:

```text
SCANNING VIDEOS
BUILDING THUMBNAILS
DETECTING CUTS
INDEX READY
```

### Step 20

Appuie:

```text
FILTR
```

Résultat:

```text
ORGANISING
SET READY
EXPORT OK
```

### Step 21

Appuie:

```text
PLAY
```

Résultat:

```text
Chromium kiosk launches
VIDZ PLAY LITE loads media-index.json
HDMI output plays video
audio source is FILE, MIC or LINE IN
```

### Step 22

Appuie:

```text
BLACK / STOP
```

Résultat:

```text
video cuts to black
playback stops or returns to safe state
```

## Diagnostic Rapide

### Rien Ne S'allume

Vérifier:

```text
power supply
USB-C cable
Pi power LED
hub power
```

### Les Cartes Ne Montent Pas

Vérifier:

```bash
lsblk
mount
dmesg
```

### Les OLED Ne Répondent Pas

Vérifier:

```bash
i2cdetect -y 1
```

Puis:

```text
SDA/SCL inversés ?
GND commun ?
adresse TCA visible ?
écran sur le bon canal ?
```

### Pas D'entrée Son

Vérifier:

```bash
arecord -l
```

Puis:

```text
LINE IN branché sur la bonne entrée ?
source trop faible ?
interface reconnue ?
```

### Vidéo Saccadée

Vérifier:

```text
Active Cooler monté
boîtier ventilé
vidéos trop lourdes
carte vidéo trop lente
USB hub alimenté
```

## Version Prototype Recommandée

Ne cherche pas à faire la belle façade d'abord.

Ordre idéal:

```text
1. Pi nu sur table
2. cartes USB reconnues
3. SCAN fonctionne
4. FILTR fonctionne
5. PLAY fonctionne sur HDMI
6. boutons fonctionnent
7. OLED fonctionnent
8. audio LINE IN / MIC fonctionne
9. montage dans boîte
10. façade finale
```

## Phrase De Fabrication

Si une étape ne marche pas sur la table, elle ne marchera pas mieux dans le boîtier.

Construis d'abord l'instrument ouvert.
Ferme la boîte seulement quand la chaîne répond:

```text
SCAN -> FILTR -> PLAY
```
