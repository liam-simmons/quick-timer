import math

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("Notify", "0.7")
gi.require_foreign("cairo")
from gi.repository import Gdk, Gtk, Notify

from .audio import AlarmStatus, play_alarm, stop_alarm
from .time_utils import format_remaining_time
from .worker import WorkerThread


class MainWindow(Gtk.Window):
  def __init__(self, duration_seconds, audio_dir, sound_path=None, volume=1.0, silent=False):
    super().__init__(title="Quick Timer")
    self.audio_dir = audio_dir
    self.sound_path = sound_path
    self.volume = volume
    self.silent = silent
    self.total_seconds = max(float(duration_seconds), 0.001)
    self.progress_fraction = 1.0
    self.finish_notification = None
    self.timer_finished = False

    self.set_default_size(620, 360)
    self.set_resizable(False)
    self.set_border_width(24)
    self._apply_styles()

    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    self.add(self.box)

    self.circle_overlay = Gtk.Overlay()
    self.box.add(self.circle_overlay)

    self.circle_area = Gtk.DrawingArea()
    self.circle_area.set_size_request(260, 260)
    self.circle_area.connect("draw", self._draw_circle)
    self.circle_overlay.add(self.circle_area)

    self.count_down_label = Gtk.Label(format_remaining_time(self.total_seconds))
    self.count_down_label.set_halign(Gtk.Align.CENTER)
    self.count_down_label.set_valign(Gtk.Align.CENTER)
    self.count_down_label.get_style_context().add_class("countdown-label")
    self.circle_overlay.add_overlay(self.count_down_label)

    self.controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.controls_box.set_halign(Gtk.Align.CENTER)
    self.box.add(self.controls_box)

    self.pause_button = Gtk.Button(label="Pause")
    self.pause_button.connect("clicked", self.pause_clicked)
    self.controls_box.add(self.pause_button)

    self.mute_button = Gtk.Button(label="Shut up")
    self.mute_button.connect("clicked", self.button_clicked)
    self.controls_box.add(self.mute_button)

    self.close_button = Gtk.Button(label="Close")
    self.close_button.connect("clicked", self.close_clicked)
    self.controls_box.add(self.close_button)

    self.connect("destroy", self.on_quit)
    self.connect("key-press-event", self.on_key_press)
    self.connect("focus-in-event", self.on_focus_in)
    self.connect("window-state-event", self.on_window_state_event)

    self.worker = WorkerThread(self, duration_seconds)
    self.worker.start()

  def _apply_styles(self):
    provider = Gtk.CssProvider()
    provider.load_from_data(
      b"""
      window {
        background: #f4f7fb;
      }

      label.countdown-label {
        color: #1f2937;
        font-size: 40px;
        font-weight: 700;
      }

      button {
        background: #ffffff;
        color: #1f2937;
        border-color: #cbd5e1;
        border-radius: 10px;
        font-weight: 700;
        padding: 8px 14px;
      }
      """
    )

    screen = self.get_screen() or Gdk.Screen.get_default()
    if screen is None:
      return

    Gtk.StyleContext.add_provider_for_screen(
      screen,
      provider,
      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

  def _draw_circle(self, widget, cr):
    width = widget.get_allocated_width()
    height = widget.get_allocated_height()

    center_x = width / 2
    center_y = height / 2
    thickness = 14
    radius = (min(width, height) / 2) - thickness - 4

    cr.set_source_rgb(1.0, 1.0, 1.0)
    cr.arc(center_x, center_y, radius + 4, 0, 2 * math.pi)
    cr.fill()

    cr.set_line_width(thickness)
    cr.set_source_rgb(0.84, 0.88, 0.93)
    cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
    cr.stroke()

    if self.progress_fraction > 0:
      start_angle = -math.pi / 2
      end_angle = start_angle + (2 * math.pi * self.progress_fraction)
      cr.set_source_rgb(0.10, 0.56, 0.95)
      cr.arc(center_x, center_y, radius, start_angle, end_angle)
      cr.stroke()

    return False

  def initial_show(self):
    self.show_all()
    self.mute_button.hide()
    self.close_button.hide()

  def show_finish_controls(self):
    self.timer_finished = True
    self.mute_button.show()
    self.close_button.show()
    self.pause_button.hide()

  def show_finish_notification(self, message="The countdown is complete."):
    title = "Timer Finished"

    if self.finish_notification is None:
      self.finish_notification = Notify.Notification.new(title, message)
    else:
      self.finish_notification.update(title, message)

    self.finish_notification.set_timeout(Notify.EXPIRES_NEVER)
    self.finish_notification.show()

  def clear_finish_notification(self):
    if self.finish_notification is None:
      return

    try:
      self.finish_notification.close()
    except Exception:
      pass

    self.finish_notification = None

  def button_clicked(self, widget):
    stop_alarm()

  def close_clicked(self, widget):
    self.close()

  def focus_window(self):
    self.deiconify()
    self.present_with_time(Gdk.CURRENT_TIME)
    self.present()

    gdk_window = self.get_window()
    if gdk_window is not None:
      gdk_window.focus(Gdk.CURRENT_TIME)

    self.grab_focus()

  def on_timer_finished(self):
    self.show_finish_controls()
    alarm_status = play_alarm(
      self.audio_dir,
      sound_path=self.sound_path,
      volume=self.volume,
      silent=self.silent,
    )
    message = "The countdown is complete."

    if alarm_status == AlarmStatus.FALLBACK:
      message = "The countdown is complete. No alarm file could be used, so a fallback tone was played."
    elif alarm_status == AlarmStatus.NONE:
      message = "The countdown is complete, but no alarm sound could be played."
    elif alarm_status == AlarmStatus.SILENT:
      message = "The countdown is complete."

    self.show_finish_notification(message)
    self.focus_window()
    return False

  def pause_clicked(self, widget):
    paused = not self.worker.is_paused()
    self.worker.set_paused(paused)
    self.pause_button.set_label("Resume" if paused else "Pause")

  def on_key_press(self, widget, event):
    if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
      self.button_clicked(self.mute_button)
      return True

    if event.keyval == Gdk.KEY_Escape and self.timer_finished:
      self.close()
      return True

    return False

  def on_focus_in(self, widget, event):
    self.clear_finish_notification()
    return False

  def on_window_state_event(self, widget, event):
    if event.new_window_state & Gdk.WindowState.FOCUSED:
      self.clear_finish_notification()

    return False

  def update_progress(self):
    self.count_down_label.set_text(self.worker.display_time)
    self.progress_fraction = min(
      1.0,
      max(0.0, self.worker.get_time_left() / self.total_seconds),
    )
    self.circle_area.queue_draw()
    return False

  def on_quit(self, widget):
    self.worker.done = True
    self.clear_finish_notification()
    Notify.uninit()
    Gtk.main_quit()


def run_app(duration_seconds, audio_dir, sound_path=None, volume=1.0, silent=False):
  Notify.init("Quick Timer")
  window = MainWindow(duration_seconds, audio_dir, sound_path=sound_path, volume=volume, silent=silent)
  window.connect("delete-event", Gtk.main_quit)
  window.initial_show()
  Gtk.main()
