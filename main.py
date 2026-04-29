import argparse
from pathlib import Path
import sys
from quick_timer.time_utils import parse_duration


THEMES = {
  "light": {
    "window_bg": "#f4f7fb",
    "label_fg": "#1f2937",
    "button_bg": "#ffffff",
    "button_fg": "#1f2937",
    "button_border": "#cbd5e1",
    "circle_bg": (1.0, 1.0, 1.0),
    "ring_bg": (0.84, 0.88, 0.93),
    "progress_normal": (0.10, 0.56, 0.95),
    "progress_warning": (0.93, 0.55, 0.13),
    "progress_danger": (0.89, 0.20, 0.20),
  },
  "dark": {
    "window_bg": "#111827",
    "label_fg": "#f9fafb",
    "button_bg": "#1f2937",
    "button_fg": "#f9fafb",
    "button_border": "#374151",
    "circle_bg": (0.12, 0.16, 0.22),
    "ring_bg": (0.30, 0.35, 0.43),
    "progress_normal": (0.22, 0.66, 0.96),
    "progress_warning": (0.98, 0.67, 0.16),
    "progress_danger": (0.95, 0.31, 0.31),
  },
  "high-contrast": {
    "window_bg": "#000000",
    "label_fg": "#ffffff",
    "button_bg": "#000000",
    "button_fg": "#ffffff",
    "button_border": "#ffffff",
    "circle_bg": (0.0, 0.0, 0.0),
    "ring_bg": (0.70, 0.70, 0.70),
    "progress_normal": (0.00, 0.80, 1.00),
    "progress_warning": (1.00, 0.85, 0.00),
    "progress_danger": (1.00, 0.25, 0.25),
  },
}


def _parse_args(argv):
  parser = argparse.ArgumentParser(description="Quick Timer")
  parser.add_argument("duration", help="Duration like 2m, 45s, 1h30m, or 500 (milliseconds)")
  parser.add_argument(
    "--sound",
    help="Alarm sound file to play. Relative paths are checked from the current directory and audio/.",
  )
  parser.add_argument(
    "--volume",
    type=float,
    default=1.0,
    help="Alarm volume from 0.0 to 1.0.",
  )
  parser.add_argument(
    "--silent",
    action="store_true",
    help="Show the finished notification without playing an alarm sound.",
  )
  parser.add_argument(
    "--theme",
    default="auto",
    help="Theme to use: auto, light, dark, high-contrast.",
  )
  return parser.parse_args(argv)


def _clamp_volume(volume):
  return min(1.0, max(0.0, volume))


def _resolve_theme(name):
  theme_name = name.lower()
  if theme_name == "auto":
    theme_name = "light"

  if theme_name not in THEMES:
    supported = ", ".join(["auto", *THEMES.keys()])
    raise ValueError(f"Unknown theme '{name}'. Supported values: {supported}")

  return THEMES[theme_name]


def main(argv=None):
  args = _parse_args(argv if argv is not None else sys.argv[1:])

  try:
    duration_seconds = parse_duration(args.duration)
    theme = _resolve_theme(args.theme)
  except ValueError as error:
    print(f"Error: {error}", file=sys.stderr)
    return 2

  try:
    import pygame
    from quick_timer.app import run_app

    pygame.mixer.init()
  except ImportError as error:
    print(f"Error importing runtime dependencies: {error}", file=sys.stderr)
    return 1
  except pygame.error as error:
    print(f"Error initializing audio: {error}", file=sys.stderr)
    return 1

  audio_dir = Path(__file__).resolve().parent / "audio"
  run_app(
    duration_seconds,
    audio_dir,
    sound_path=args.sound,
    volume=_clamp_volume(args.volume),
    silent=args.silent,
    theme=theme,
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
