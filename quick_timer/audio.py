from pathlib import Path
import random

import pygame


_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}


def _list_audio_files(audio_dir):
  if not audio_dir.is_dir():
    return []

  return [
    path
    for path in audio_dir.iterdir()
    if path.is_file() and path.suffix.lower() in _AUDIO_EXTENSIONS
  ]


def play_random_alarm(audio_dir):
  audio_files = _list_audio_files(Path(audio_dir))
  if not audio_files:
    return False

  selected_file = random.choice(audio_files)
  pygame.mixer.music.load(str(selected_file))
  pygame.mixer.music.play(loops=0)
  return True


def stop_alarm():
  pygame.mixer.music.stop()

