import unittest

from quick_timer.time_utils import format_remaining_time, parse_duration


class ParseDurationTests(unittest.TestCase):
  def test_parses_minutes_seconds_hours_and_milliseconds(self):
    self.assertEqual(parse_duration("2m"), 120)
    self.assertEqual(parse_duration("45s"), 45)
    self.assertEqual(parse_duration("1h30m"), 5400)
    self.assertEqual(parse_duration("500"), 0.5)

  def test_normalizes_whitespace_and_case(self):
    self.assertEqual(parse_duration(" 1H05M09S250 "), 3909.25)

  def test_rejects_empty_duration(self):
    with self.assertRaises(ValueError):
      parse_duration("")

  def test_rejects_invalid_duration(self):
    invalid_values = ["abc", "1d", "1m2h", "1000", "1.5m"]

    for value in invalid_values:
      with self.subTest(value=value):
        with self.assertRaises(ValueError):
          parse_duration(value)


class FormatRemainingTimeTests(unittest.TestCase):
  def test_formats_minutes_and_seconds(self):
    self.assertEqual(format_remaining_time(65), "01:05")
    self.assertEqual(format_remaining_time(0), "00:00")
    self.assertEqual(format_remaining_time(-1), "00:00")

  def test_rounds_up_partial_seconds(self):
    self.assertEqual(format_remaining_time(1.1), "00:02")

  def test_formats_hours_and_days(self):
    self.assertEqual(format_remaining_time(3661), "01:01:01")
    self.assertEqual(format_remaining_time(90061), "01:01:01:01")


if __name__ == "__main__":
  unittest.main()
