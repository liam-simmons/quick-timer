import argparse
from pathlib import Path
import sys
from quick_timer.time_utils import parse_duration


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
  return parser.parse_args(argv)


def _clamp_volume(volume):
  return min(1.0, max(0.0, volume))


def main(argv=None):
  args = _parse_args(argv if argv is not None else sys.argv[1:])

  try:
    duration_seconds = parse_duration(args.duration)
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
  )
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
