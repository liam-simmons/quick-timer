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


DEFAULT_THEME = {
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
}


class MainWindow(Gtk.Window):
  def __init__(self, duration_seconds, audio_dir, sound_path=None, volume=1.0, silent=False, theme=None):
    super().__init__(title="Quick Timer")
    self.audio_dir = audio_dir
    self.sound_path = sound_path
    self.volume = volume
    self.silent = silent
    self.total_seconds = max(float(duration_seconds), 0.001)
    self.progress_fraction = 1.0
    self.finish_notification = None
    self.timer_finished = False
    self.worker = None
    self.theme = theme or DEFAULT_THEME

    self.set_default_size(620, 360)
    self.set_size_request(360, 320)
    self.set_resizable(True)
    self.set_border_width(24)
    self._apply_styles()

    self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
    self.add(self.box)

    self.circle_overlay = Gtk.Overlay()
    self.circle_overlay.set_hexpand(True)
    self.circle_overlay.set_vexpand(True)
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

    self.restart_button = Gtk.Button(label="Restart")
    self.restart_button.connect("clicked", self.restart_clicked)
    self.controls_box.add(self.restart_button)

    self.mute_button = Gtk.Button(label="Stop sound")
    self.mute_button.connect("clicked", self.button_clicked)
    self.controls_box.add(self.mute_button)

    self.close_button = Gtk.Button(label="Close")
    self.close_button.connect("clicked", self.close_clicked)
    self.controls_box.add(self.close_button)

    self.connect("destroy", self.on_quit)
    self.connect("key-press-event", self.on_key_press)
    self.connect("focus-in-event", self.on_focus_in)
    self.connect("window-state-event", self.on_window_state_event)

    self.start_worker()

  def _apply_styles(self):
    provider = Gtk.CssProvider()
    css = f"""
      window {{
        background: {self.theme['window_bg']};
      }}

      label.countdown-label {{
        color: {self.theme['label_fg']};
        font-size: 40px;
        font-weight: 700;
      }}

      button {{
        background: {self.theme['button_bg']};
        color: {self.theme['button_fg']};
        border-color: {self.theme['button_border']};
        border-radius: 10px;
        font-weight: 700;
        padding: 8px 14px;
      }}
      """
    provider.load_from_data(css.encode("utf-8"))

    screen = self.get_screen() or Gdk.Screen.get_default()
    if screen is None:
      return

    Gtk.StyleContext.add_provider_for_screen(
      screen,
      provider,
      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

  def _progress_color(self, time_left):
    warning_seconds = min(60.0, max(5.0, self.total_seconds * 0.10))
    danger_seconds = min(10.0, max(2.0, self.total_seconds * 0.03))

    if time_left <= danger_seconds:
      return self.theme["progress_danger"]

    if time_left <= warning_seconds:
      return self.theme["progress_warning"]

    return self.theme["progress_normal"]

  def _draw_circle(self, widget, cr):
    width = widget.get_allocated_width()
    height = widget.get_allocated_height()

    center_x = width / 2
    center_y = height / 2
    thickness = 14
    radius = max(12, (min(width, height) / 2) - thickness - 4)

    circle_red, circle_green, circle_blue = self.theme["circle_bg"]
    cr.set_source_rgb(circle_red, circle_green, circle_blue)
    cr.arc(center_x, center_y, radius + 4, 0, 2 * math.pi)
    cr.fill()

    cr.set_line_width(thickness)
    ring_red, ring_green, ring_blue = self.theme["ring_bg"]
    cr.set_source_rgb(ring_red, ring_green, ring_blue)
    cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
    cr.stroke()

    if self.progress_fraction > 0:
      start_angle = -math.pi / 2
      end_angle = start_angle + (2 * math.pi * self.progress_fraction)
      red, green, blue = self._progress_color(self.worker.get_time_left())
      cr.set_source_rgb(red, green, blue)
      cr.arc(center_x, center_y, radius, start_angle, end_angle)
      cr.stroke()

    return False

  def start_worker(self):
    self.worker = WorkerThread(self, self.total_seconds)
    self.worker.start()

  def initial_show(self):
    self.show_all()
    self.mute_button.hide()
    self.close_button.hide()

  def show_finish_controls(self):
    self.timer_finished = True
    self.mute_button.show()
    self.close_button.show()
    self.pause_button.hide()

  def show_running_controls(self):
    self.timer_finished = False
    self.pause_button.show()
    self.pause_button.set_label("Pause")
    self.mute_button.hide()
    self.close_button.hide()

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

  def restart_clicked(self, widget):
    stop_alarm()
    self.clear_finish_notification()

    if self.worker is not None:
      self.worker.done = True

    self.progress_fraction = 1.0
    self.count_down_label.set_text(format_remaining_time(self.total_seconds))
    self.show_running_controls()
    self.start_worker()
    self.circle_area.queue_draw()

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
    if self.worker is not None:
      self.worker.done = True
    self.clear_finish_notification()
    Notify.uninit()
    Gtk.main_quit()


def run_app(duration_seconds, audio_dir, sound_path=None, volume=1.0, silent=False, theme=None):
  Notify.init("Quick Timer")
  window = MainWindow(
    duration_seconds,
    audio_dir,
    sound_path=sound_path,
    volume=volume,
    silent=silent,
    theme=theme,
  )
  window.connect("delete-event", Gtk.main_quit)
  window.initial_show()
  Gtk.main()
