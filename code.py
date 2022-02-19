import time
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1107
import adafruit_ds3231

displayio.release_displays()
# oled_reset = board.D9

# Use for I2C
i2c         = busio.I2C(board.SCL,board.SDA,frequency=400000)
disp_bus    = displayio.I2CDisplay(i2c, device_address=0x3C)
rtc         = adafruit_ds3231.DS3231(i2c)

# SH1107 is vertically oriented 64x128
WIDTH = 128
HEIGHT = 64
BORDER = 1

display = adafruit_displayio_sh1107.SH1107( disp_bus,
                                            width=WIDTH,
                                            height=HEIGHT,
                                            rotation=0)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

now = rtc.datetime

# Draw some label text
text1       = "{:02d}.{:02d}.{}".format(now.tm_mday,now.tm_mon,now.tm_year)
text_area   = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF, x=8, y=8)
splash.append(text_area)
text2 = "{:02d}:{:02d}:{:02d}".format(now.tm_hour,now.tm_min,now.tm_sec)
text_area2 = label.Label(
    terminalio.FONT, text=text2, scale=2, color=0xFFFFFF, x=9, y=44
)
splash.append(text_area2)

last    = time.monotonic()
display.brightness  = 0.1
while True:
    if time.monotonic() >= last + 1.0:
        now = rtc.datetime
        text1       = "{:02d}.{:02d}.{}".format(now.tm_mday,now.tm_mon,now.tm_year)
        text_area   = label.Label(terminalio.FONT, text=text1, color=0xFFFFFF, x=8, y=8)
        splash[0]   = text_area
        text2 = "{:02d}:{:02d}:{:02d}".format(now.tm_hour,now.tm_min,now.tm_sec)
        text_area2 = label.Label(
            terminalio.FONT, text=text2, scale=2, color=0xFFFFFF, x=9, y=44
        )
        splash[1]   = text_area2
        last        = time.monotonic()
