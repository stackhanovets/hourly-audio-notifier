```text
usage: hourly-audio-notifier.py [-h] -i INPUT -f FFPLAY
                                [-a ACTIVE [ACTIVE ...]] [-o OFFSET]

The script automatically finds, randomizes and plays the corresponding hourly
notification based on your local time.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input directory. Note: the notification file name must
                        be ending with the pattern: '< two-digit hour number
                        >.< an extension >'. E.g.: 'Iowa-01.ogg' or 'Vault
                        21.mp3' but not '2021.mp3' or 'Hour-1.ogg'.
  -f FFPLAY, --ffplay FFPLAY
                        Path to the FFplay binary.
  -a ACTIVE [ACTIVE ...], --active ACTIVE [ACTIVE ...]
                        The hours when the program is active (default: 7 a.m.
                        till 10 p.m.).
  -o OFFSET, --offset OFFSET
                        Use a custom offset instead of your local time. It
                        affects the notification file selection only.

You also have to download the FFplay binary suitable with your system:
https://www.ffmpeg.org/download.html
```
