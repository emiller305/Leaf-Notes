"""
2025 Senior Design
E-Ink Display and Raspberry Pi Interface
Elisa Miller
"""

#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in52
import time
from time import sleep
from datetime import datetime, date # display current time
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont
import traceback
#grandparent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
#sys.path.append(grandparent_dir)
#from gen_audio_stream_sd import get_amplitude

logging.basicConfig(level=logging.DEBUG)
volume_filename = "/home/pi/senior-design-2025/display/volume.txt"
if os.path.exists(volume_filename):
    with open(volume_filename, "w") as f:
        f.write("Volume: 1")
try:
    # logging.info("epd3in52 Demo")
    epd = epd3in52.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.display_NUM(epd.WHITE)
    epd.lut_GC()
    epd.refresh()

    epd.send_command(0x50)
    epd.send_data(0x17)
    time.sleep(2)
    
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)

    logging.info("Clear...")
    epd.Clear()

    # add code to display welcome screen and current time
    logging.info("Displaying welcome screen and current time...")
    try:
        while True:
            #get_amplitude()
            # create a new image for the welcome screen - horizontal
            welcome_image = Image.new('1', (epd.height, epd.width), 255)  # 255: white background
            draw = ImageDraw.Draw(welcome_image)
            # draw welcome message
            draw.text((50, 0), "Welcome to", font=font24, fill=0)
            draw.text((50, 30), "LeafNotes", font=font30, fill=0)
            # draw current date and time
            now = datetime.now()
            # set timezone
            now = datetime.now(ZoneInfo("America/New_York"))
            print("Time in New York:", now.strftime("%Y-%m-%d %H:%M:%S"))
            current_time = now.strftime("%A, %B %d, %Y\n%I:%M %p")
            draw.text((10, 100), current_time, font=font18, fill=0)
            # display current volume
            if os.path.exists(volume_filename):
                with open(volume_filename, "r") as f:
                    volume = f.read().strip()
            else:
                volume = "Volume: 1"
            if volume == "Volume: 0":
                volume = "Volume: OFF"
            draw.text((10, 150), volume, font=font18, fill=0)
            # display the image
            epd.display(epd.getbuffer(welcome_image))
            # epd.lut_GC()
            epd.lut_DU() # quick refresh
            epd.refresh()
            time.sleep(0.1)
    except Exception as e:
        print(e)
        logging.info("Interrupted by user. Going to sleep...")
        epd.sleep()
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
