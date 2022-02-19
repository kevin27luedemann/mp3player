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
import audiomixer
import rtc
import keypad
import os

displayio.release_displays()
keys        = keypad.Keys(  (board.D9,board.D6,board.D5),
                            value_when_pressed=False,
                            pull=True,
                            interval=0.00001)

#Init I2C devices
i2c         = busio.I2C(board.SCL,board.SDA,frequency=400000)
disp_bus    = displayio.I2CDisplay(i2c, device_address=0x3C)
ds3231      = adafruit_ds3231.DS3231(i2c)
r           = rtc.RTC()
r.datetime = ds3231.datetime

#Init SD card
spi     = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
spi.try_lock()
spi.configure(baudrate=5000000)
spi.unlock()
#print(spi.frequency)
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
now = r.datetime
disp        = displayio.Group()
header      = "{:02d}.{:02d}.{} {:02d}:{:02d}".format(  now.tm_mday,
                                                        now.tm_mon,
                                                        now.tm_year,
                                                        now.tm_hour,
                                                        now.tm_min)
header_area = label.Label(terminalio.FONT, text=header, color=0xFFFFFF, x=8, y=8)
disp.append(header_area)

progress  = label.Label(terminalio.FONT,
                        text="Playing",
                        color=0xFFFFFF,
                        x=8, y=24,scale=2)
disp.append(progress)
display.show(disp)

#Init and play sound
audio       = audiobusio.I2SOut(board.D11, board.D12, board.D13)

os.chdir("/sd/p1")
files       = os.listdir()
print(files)
counter     = 0
maxcounter  = len(files)-1
fi          = open(files[counter],"rb")
print(files[counter])
#if files[counter][-3:] == "mp3":
#    decoder     = audiomp3.MP3Decoder(fi)
#elif files[counter][-3:] == "wav":
decoder     = audiocore.WaveFile(fi)
print(decoder.sample_rate)
print(decoder.channel_count)
print(decoder.bits_per_sample)

mixer       = audiomixer.Mixer( voice_count=1,
                                sample_rate=decoder.sample_rate,
                                channel_count=decoder.channel_count,
                                bits_per_sample=decoder.bits_per_sample,
                                samples_signed=True)
mixer.voice[0].level    = 0.1
audio.play(mixer)
audio.pause()

player  = label.Label(terminalio.FONT,
                        text=files[0][:-4],
                        color=0xFFFFFF,
                        x=8, y=48,scale=1)
disp.append(player)
disp[1].text = "Pause"

mixer.voice[0].play(decoder,loop=True)

last    = time.monotonic()
while True:
    key_event = keys.events.get()
    if key_event != None:
        if key_event.key_number == 0 and key_event.released:
            if audio.playing and not(audio.paused):
                disp[1].text = "Pause"
                audio.pause()
            else:
                disp[1].text = "Playing"
                time.sleep(0.1)
                audio.resume()
        elif key_event.key_number == 1 and key_event.released:
            if audio.playing and not(audio.paused):
                audio.pause()
            counter += 1
            if counter >maxcounter:
                counter = 0
            fi.close()
            fi          = open(files[counter],"rb")
            if files[counter][-3:] == "mp3":
                decoder     = audiomp3.MP3Decoder(fi)
            elif files[counter][-3:] == "wav":
                decoder     = audiocore.WaveFile(fi)
            mixer.voice[0].play(decoder,loop=True)
            player.text = files[counter][:-4]
            audio.resume()
            disp[1].text = "Playing"
    if time.monotonic() >= last + 60.0 and (audio.paused or not(audio.playing)):
        last        = time.monotonic()
        now = r.datetime
        text1       = "{:02d}.{:02d}.{} {:02d}:{:02d}".format(  now.tm_mday,
                                                                now.tm_mon,
                                                                now.tm_year,
                                                                now.tm_hour,
                                                                now.tm_min)
        disp[0].text  = text1
    time.sleep(0.005)
