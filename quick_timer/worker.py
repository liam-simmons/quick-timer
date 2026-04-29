import threading
import time

from gi.repository import GObject

from .time_utils import format_remaining_time


FRAME_INTERVAL_SECONDS = 1 / 60


class WorkerThread(threading.Thread):
  def __init__(self, delegate, duration_seconds):
    super().__init__(daemon=True)
    self.delegate = delegate
    self.lock = threading.Lock()
    self.paused = False
    self.done = False
    self.time_left = max(float(duration_seconds), 0.0)
    self.display_time = format_remaining_time(self.time_left)

  def set_paused(self, paused):
    with self.lock:
      self.paused = paused

  def is_paused(self):
    with self.lock:
      return self.paused

  def get_time_left(self):
    with self.lock:
      return self.time_left

  def run(self):
    last_tick = time.monotonic()

    while True:
      if self.done:
        print("Background thread shutting down cleanly")
        break

      now = time.monotonic()
      elapsed = now - last_tick
      last_tick = now

      with self.lock:
        if not self.paused:
          self.time_left = max(0.0, self.time_left - elapsed)

        local_time_left = self.time_left

      self.display_time = format_remaining_time(local_time_left)
      GObject.idle_add(self.delegate.update_progress)

      if local_time_left <= 0:
        GObject.idle_add(self.delegate.on_timer_finished)
        break

      time.sleep(FRAME_INTERVAL_SECONDS)

