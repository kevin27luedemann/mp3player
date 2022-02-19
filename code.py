import time
import board
import busio
import digitalio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_sh1107
import adafruit_ds3231
import adafruit_sdcard
import storage
import audiobusio
import audiocore
import audiomp3

displayio.release_displays()
#Init buttons
A           = digitalio.DigitalInOut(board.D9)
A.direction = digitalio.Direction.INPUT
A.pull      = digitalio.Pull.UP
B           = digitalio.DigitalInOut(board.D6)
B.direction = digitalio.Direction.INPUT
B.pull      = digitalio.Pull.UP
C           = digitalio.DigitalInOut(board.D5)
C.direction = digitalio.Direction.INPUT
C.pull      = digitalio.Pull.UP

#Init I2C devices
i2c         = busio.I2C(board.SCL,board.SDA,frequency=400000)
disp_bus    = displayio.I2CDisplay(i2c, device_address=0x3C)
rtc         = adafruit_ds3231.DS3231(i2c)

#Init SD card
spi     = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs_SD   = digitalio.DigitalInOut(board.D25)
sdcard  = adafruit_sdcard.SDCard(spi, cs_SD)
vfs     = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Init Display
WIDTH = 128
HEIGHT = 64
BORDER = 1

display = adafruit_displayio_sh1107.SH1107( disp_bus,
                                            width=WIDTH,
                                            height=HEIGHT,
                                            rotation=0)

display.brightness  = 0.1

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

#Init and play sound
wave_file   = open("StreetChicken.wav", "rb")
wave        = audiocore.WaveFile(wave_file)
audio       = audiobusio.I2SOut(board.D11, board.D12, board.D13)

mp3file     = open("begins.mp3","rb")
decoder = audiomp3.MP3Decoder(mp3file)


#audio.play(wave)
#audio.play(decoder)
#while audio.playing:
#    pass

last    = time.monotonic()
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
