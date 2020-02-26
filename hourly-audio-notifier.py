#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import random
import argparse
import subprocess
import datetime as dt
from time import sleep


def _parse_args():
    argument_parser = argparse.ArgumentParser(description="The script automatically finds, randomizes and plays the "
                                                          "corresponding hourly notification based on your local time.",
                                              epilog="You also have to download the FFplay binary suitable with your "
                                                     "system: https://www.ffmpeg.org/download.html")
    argument_parser.add_argument("-i", "--input", required=True,
                                 help="Input directory. Note: the notification file name must be ending "
                                      "with the pattern: '< two-digit hour number >.< an extension >'.\n "
                                      "E.g.: 'Iowa-01.ogg' or 'Vault 21.mp3' but not '2021.mp3' or 'Hour-1.ogg'.")
    argument_parser.add_argument("-f", "--ffplay", required=True,
                                 help="Path to the FFplay binary.")
    argument_parser.add_argument("-a", "--active", default=[7, 22], nargs="+",
                                 help="The hours when the program is active (default: 7 a.m. till 10 p.m.).")
    argument_parser.add_argument("-o", "--offset", default=0, type=int,
                                 help="Use a custom offset instead of your local time. "
                                      "It affects the notification file selection only.")
    return argument_parser.parse_args()


def is_hour(x):
    return str(x).isnumeric() and int(x) in range(0, 24)


def _parse_active_hours(*args):
    if len(args) < 2:
        raise ValueError("Exactly two values are required to pass as active hours!")
    if len(args) > 2:
        print("Using the only two first values passed as active hour boundaries!")
    minmax = []
    for arg in args[:2]:
        if not is_hour(arg):
            raise ValueError("Not an hour: '{}'".format(arg))
        minmax.append(int(arg))
    if minmax[-1] < minmax[0]:  # E.g. [21, 3]
        minmax[-1] += 24
    out = [[i - 24, i][i < 24] for i in list(range(*minmax)) + [minmax[-1]]]
    return out


def find_all_directory_files(dir_name: str):
    out = []
    for root, dirs, files in os.walk(dir_name):
        for file in files:
            out.append(os.path.join(root, file))
    return sorted(out)


def parse_hour(file: str):
    matches = re.findall("([0-9]+)$", os.path.splitext(os.path.basename(file))[0])
    if len(matches) > 0:
        hour = int(matches[0])
        if len(matches[0]) == 2 and is_hour(hour):
            return hour
    return -1


def is_audio_notification(file: str):
    _AUDIO_EXTENSIONS = ("wav", "mp3", "ogg")
    extension = os.path.splitext(os.path.basename(file))[-1].strip(".").lower()
    return extension in _AUDIO_EXTENSIONS and parse_hour(file) >= 0


def sleep_until(dt_: dt.datetime):
    print("Paused until {} ({} left).".format(str(dt_), dt_ - dt.datetime.now()))
    sleep((dt_ - dt.datetime.now()).total_seconds())


def play_audio(file: str):
    _now = dt.datetime.now()
    print("Playing '{}' at {}:{}:{}.{}".format(file, _now.hour, _now.minute, _now.second, _now.microsecond))
    _ = subprocess.getoutput("{} -nodisp -autoexit {}".format(ffplayPath, file))


if __name__ == '__main__':
    namespace = _parse_args()
    inputDir = namespace.input
    offsetHours = namespace.offset
    ffplayPath = namespace.ffplay
    activeHours = namespace.active

    print("Scanning the audio notification files...")
    all_notifications = sorted(list(filter(is_audio_notification, find_all_directory_files(inputDir))))
    print("{} items found!".format(len(all_notifications)))
    active_hour_range = _parse_active_hours(*activeHours)

    used_notifications = dict()
    while True:
        now = dt.datetime.now()
        future = dt.datetime(now.year, now.month, now.day, now.hour) + dt.timedelta(hours=1)
        next_hour = future.hour
        if next_hour not in active_hour_range:
            next_datetime = dt.datetime(now.year, now.month, now.day, active_hour_range[0]) - dt.timedelta(hours=1)
            if active_hour_range[0] < now.hour:
                next_datetime += dt.timedelta(days=1)
            print("The active time is over.")
            sleep_until(next_datetime)
            continue
        notification_hour = (future + dt.timedelta(hours=offsetHours)).hour
        # Auto negotiation for the JST offset:
        # int(dt.datetime.now(dt.timezone.utc).astimezone().utcoffset().total_seconds() / 3600) + 9
        hourly_used_notifications = used_notifications.get(str(notification_hour).zfill(2))
        if hourly_used_notifications is None:
            hourly_used_notifications = []
        next_hour_notifications = [i for i in all_notifications if
                                   parse_hour(i) == notification_hour and i not in hourly_used_notifications]
        if len(next_hour_notifications) == 0:
            hourly_used_notifications = []
            next_hour_notifications = [i for i in all_notifications if parse_hour(i) == notification_hour]
        chosen_notification = random.choice(next_hour_notifications)
        print("Next playing: '{}'".format(chosen_notification))
        sleep_until(future)
        play_audio(chosen_notification)
        hourly_used_notifications.append(chosen_notification)
