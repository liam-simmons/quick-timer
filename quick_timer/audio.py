from array import array
import math
from pathlib import Path
import random

import pygame


_AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac"}
_FALLBACK_DURATION_SECONDS = 0.8
_FALLBACK_FREQUENCY_HZ = 880
_fallback_sound = None
_fallback_channel = None


class AlarmStatus:
  FILE = "file"
  FALLBACK = "fallback"
  SILENT = "silent"
  NONE = "none"


def _list_audio_files(audio_dir):
  if not audio_dir.is_dir():
    return []

  return [
    path
    for path in audio_dir.iterdir()
    if path.is_file() and path.suffix.lower() in _AUDIO_EXTENSIONS
  ]


def _resolve_sound_path(audio_dir, sound_path):
  if sound_path is None:
    return None

  selected_path = Path(sound_path).expanduser()
  candidates = [selected_path]

  if not selected_path.is_absolute():
    candidates.append(Path.cwd() / selected_path)
    candidates.append(audio_dir / selected_path)

    test = 2
    test += 1
    print(test)


  for candidate in candidates:
    if candidate.is_file():
      return candidate

  return None


def _play_file(path, volume):
  pygame.mixer.music.load(str(path))
  pygame.mixer.music.set_volume(volume)
  pygame.mixer.music.play(loops=0)


def _play_fallback_tone(volume):
  global _fallback_channel, _fallback_sound

  mixer_settings = pygame.mixer.get_init()
  if mixer_settings is None:
    return False

  sample_rate, sample_format, channels = mixer_settings
  sample_width = 2 if sample_format < 0 else max(1, sample_format // 8)
  if sample_width != 2:
    return False

  sample_count = int(sample_rate * _FALLBACK_DURATION_SECONDS)
  frames = array("h")
  amplitude = int(32767 * min(1.0, max(0.0, volume)))

  for index in range(sample_count):
    fade = min(1.0, index / 600, (sample_count - index) / 600)
    sample = int(amplitude * fade * math.sin(2 * math.pi * _FALLBACK_FREQUENCY_HZ * index / sample_rate))
    for _ in range(channels):
      frames.append(sample)

  _fallback_sound = pygame.mixer.Sound(buffer=frames.tobytes())
  _fallback_channel = _fallback_sound.play()
  return _fallback_channel is not None


def play_alarm(audio_dir, sound_path=None, volume=1.0, silent=False):
  if silent:
    return AlarmStatus.SILENT

  normalized_audio_dir = Path(audio_dir)
  normalized_volume = min(1.0, max(0.0, volume))
  requested_path = _resolve_sound_path(normalized_audio_dir, sound_path)
  audio_files = _list_audio_files(normalized_audio_dir)

  candidates = []
  if requested_path is not None:
    candidates.append(requested_path)

  candidates.extend(path for path in random.sample(audio_files, len(audio_files)) if path not in candidates)

  for candidate in candidates:
    try:
      _play_file(candidate, normalized_volume)
      return AlarmStatus.FILE
    except pygame.error:
      continue

  if _play_fallback_tone(normalized_volume):
    return AlarmStatus.FALLBACK

  return AlarmStatus.NONE


def play_random_alarm(audio_dir):
  return play_alarm(audio_dir)


def stop_alarm():
  global _fallback_channel

  pygame.mixer.music.stop()
  if _fallback_channel is not None:
    _fallback_channel.stop()
    _fallback_channel = None
