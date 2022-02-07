from math import floor
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import time
import pygame
import sys

from countdown_thread import WorkerThread
import helpers

start_time = time.time()
count_down = helpers.parse_countdown_entry(sys.argv[1])
end_time = start_time + count_down

pygame.mixer.init()

class MainWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Quick Timer")

    self.set_border_width(20)

    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
    self.add(self.box)
  
    self.count_down_label = Gtk.Label(str(count_down))
    self.box.add(self.count_down_label)

    self.button = Gtk.Button(label="Shut up")
    self.button.connect("clicked", self.button_clicked)
    self.box.add(self.button)

    # Connect the destroy event so that we can set the done flag and
    # terminate the worker cleanly.
    self.connect("destroy", self.on_quit)

    # Kick off the background thread.
    self.worker = WorkerThread(self)
    self.worker.start()

  def initial_show(self):
    window.show_all()
    self.button.hide()

  def show_button(self):
    self.button.show()
  
  def button_clicked(self, widget):
    helpers.stop_noise()

  def update_progress(self):
    self.count_down_label.set_text(self.worker.count_down)

    return False

  def on_quit(self, widget):
        self.worker.done = True
        Gtk.main_quit()

if __name__ == '__main__':
  window = MainWindow()
  window.connect('delete-event', Gtk.main_quit)
  window.initial_show()
  Gtk.main()
