
import threading
import random
from gi.repository import GObject
from plyer import notification
import time
import sys

import helpers

start_time = time.time()
count_down = helpers.parse_countdown_entry(sys.argv[1])
end_time = start_time + count_down

class WorkerThread(threading.Thread):
  def __init__(self, delegate):
    threading.Thread.__init__(self)
    self.delegate = delegate
    self.count_down = self.get_time_left()
    self.done = False
    self.played_noise = False

  def get_time_left(self):
    time_left = max(float(0), end_time - time.time())

    return helpers.format_time(time_left)

  def run(self):
    while True:
      if self.done:
          print('Background thread shutting down cleanly')
          break

      self.count_down = self.get_time_left()

      # Ask the main thread to update the GUI when it has time.
      GObject.idle_add(self.delegate.update_progress)

      if not self.played_noise and time.time() > end_time:
        helpers.play_noise()
        self.played_noise = True

        notif_title = 'Timer Ended'
        notif_message = ''

        notification.notify(title=notif_title, message=notif_message, timeout=10, toast=False)

        GObject.idle_add(self.delegate.show_button)
        break

      # Sleep for a little bit ...
      time.sleep(random.uniform(0.01, 0.1))
