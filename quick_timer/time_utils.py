import re
from math import ceil


_DURATION_PATTERN = re.compile(
  r"^(?:(?P<hours>\d{1,3})h)?(?:(?P<minutes>\d{1,2})m)?(?:(?P<seconds>\d{1,2})s)?(?:(?P<milliseconds>\d{1,3}))?$"
)


def parse_duration(entry):
  normalized = entry.strip().lower()
  match = _DURATION_PATTERN.fullmatch(normalized)

  if not match:
    raise ValueError("Invalid duration format. Examples: 2m, 45s, 1h30m, 500")

  if not any(match.group(name) for name in ("hours", "minutes", "seconds", "milliseconds")):
    raise ValueError("Duration cannot be empty.")

  time_total = 0.0
  if match.group("hours"):
    time_total += int(match.group("hours")) * 60 * 60
  if match.group("minutes"):
    time_total += int(match.group("minutes")) * 60
  if match.group("seconds"):
    time_total += int(match.group("seconds"))
  if match.group("milliseconds"):
    time_total += int(match.group("milliseconds")) / 1000

  return time_total


def format_remaining_time(time_left):
  total_seconds = 0 if time_left <= 0 else ceil(time_left)

  days = total_seconds // (60 * 60 * 24)
  left = total_seconds - (days * 60 * 60 * 24)

  hours = left // (60 * 60)
  left -= hours * 60 * 60

  minutes = left // 60
  seconds = left - (minutes * 60)

  if days > 0:
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"

  if hours > 0:
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

  return f"{minutes:02d}:{seconds:02d}"

