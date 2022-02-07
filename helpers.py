import re
import pygame
from math import floor
import os 


def parse_countdown_entry(entry):
  regex = re.compile(r'([0-9]{1,3}h)?([0-9]{1,2}m)?([0-9]{1,2}s)?([0-9]{1,3})?$')
  matches = regex.finditer(entry)

  time_total = 0

  for match in matches:
    for i in range (1, regex.groups):
      if match.group(i):
        group_text = match.group(i)

        time_type = group_text[-1] #h,m,s
        time_value = group_text[:-1]

        if time_type == 'h':
            time_total += int(time_value) * 60*60
        elif time_type == 'm':
            time_total += int(time_value) * 60
        elif time_type == 's':
            time_total += int(time_value)
        elif time_type == '':
            time_total += float(time_value)/1000

  return time_total

def play_noise():
  dir_path = os.path.dirname(os.path.realpath(__file__))

  pygame.mixer.music.load(dir_path + '/audio/noise.mp3')
  pygame.mixer.music.play(loops=0)

def stop_noise():
  pygame.mixer.music.stop()

def format_time(time):
  milliseconds = floor((time%1) * 1000)

  left = floor(time)
    
  seconds_in_day = 60*60*24
  days = floor(left / seconds_in_day)
  left-= (seconds_in_day * days)

  seconds_in_hour = 60*60
  hours = floor(left / seconds_in_hour)
  left-= (seconds_in_hour * hours)

  seconds_in_minute = 60
  minutes = floor(left / seconds_in_minute)
  left-= (seconds_in_minute * minutes)

  seconds = left

  fill_day = str(days).zfill(2)
  fill_hour = str(hours).zfill(2)
  fill_minute = str(minutes).zfill(2)
  fill_second = str(seconds).zfill(2)
  fill_millisecond = str(milliseconds).zfill(3)

  return fill_day + ' ' + fill_hour + ' ' + fill_minute + ' ' + fill_second + ' ' + fill_millisecond