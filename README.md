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

## Install (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3-pygame
```

## Run

Use system Python:

```bash
/usr/bin/python3 main.py 2m
```

If you created the launcher script previously:

```bash
timer 2m
```

## Duration Format

- `2m`
- `45s`
- `1h30m`
- `500` (milliseconds)

## Troubleshooting

If you see `ImportError: No module named 'gi._gi_cairo'`:

```bash
sudo apt install -y python3-gi-cairo
```
