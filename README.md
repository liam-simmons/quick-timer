# Quick Timer

Desktop countdown timer built with GTK, with:

- Circular visual countdown
- Pause/resume controls
- Random alarm sound from `audio/`
- Finish notification + auto-focus
- Keyboard shortcuts (`Enter`/`Space` to stop sound, `Esc` to close when finished)

## Project Structure

```text
.
├── main.py                 # CLI entrypoint
├── quick_timer/
│   ├── app.py              # GTK window + UI behavior
│   ├── worker.py           # countdown background thread
│   ├── time_utils.py       # duration parsing + display formatting
│   └── audio.py            # random audio selection + playback
└── audio/                  # alarm sounds
```

## Install

Quick Timer is a Linux desktop app built on GTK 3, libnotify, and pygame.

### Debian/Ubuntu

```bash
sudo apt update
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-notify-0.7 python3-pygame
```

### Fedora

```bash
sudo dnf install -y python3-gobject gtk3 libnotify python3-pygame
```

### Arch Linux

```bash
sudo pacman -S --needed python-gobject gtk3 libnotify python-pygame
```

macOS and Windows are not currently supported because the app depends on GTK and libnotify integration.

## Run

Use system Python:

```bash
/usr/bin/python3 main.py 2m
```

If you created the launcher script previously:

```bash
timer 2m
```

Choose a specific alarm file:

```bash
/usr/bin/python3 main.py 2m --sound audio/cow-moo.mp3
```

Adjust volume or run silently:

```bash
/usr/bin/python3 main.py 2m --volume 0.5
/usr/bin/python3 main.py 2m --silent
```

## Duration Format

- `2m`
- `45s`
- `1h30m`
- `500` (milliseconds)

## Controls

- `Pause` pauses the countdown.
- `Resume` continues a paused countdown.
- `Restart` starts the same timer again from its original duration.
- `Stop sound` silences the alarm after the timer finishes.
- `Close` exits the timer.
- `Enter` or `Space` stops the alarm sound.
- `Esc` closes the window after the timer has finished.

## Troubleshooting

If you see `ImportError: No module named 'gi._gi_cairo'`:

```bash
sudo apt install -y python3-gi-cairo
```

If no audio file can be loaded from `audio/`, Quick Timer plays a short built-in fallback tone instead.
