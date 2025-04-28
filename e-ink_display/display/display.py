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

logging.basicConfig(level=logging.DEBUG)
volume_filename = "/home/pi/senior-design-2025/display/volume.txt"
stim_filename = "/home/pi/senior-design-2025/display/stimulus.txt"
stim = "0"
if os.path.exists(volume_filename):
    with open(volume_filename, "w") as f:
        f.write("Volume: 1")
if os.path.exists(stim_filename):
    with open(stim_filename, "w") as f:
        f.write("0")
try:
    
    epd = epd3in52.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.display_NUM(epd.WHITE)
    epd.lut_GC()
    epd.refresh()

    epd.send_command(0x50)
    epd.send_data(0x17)
    time.sleep(2)
    
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font20 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
    font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 30)
    font50 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 50)

    logging.info("Clear...")
    epd.Clear()
    
    # 1 = plant is happy, 0 = plant needs water
    plant_status = 0
    logging.info("Setting Plant Status...")
    
    # display welcome screen and current time
    logging.info("Displaying welcome screen and current time...")
    try:
        # read logo bmp file
        logging.info("read logo bmp file")
        logo_bmp = Image.open(os.path.join(picdir, 'logo-bw.bmp'))

        # read volume bmp files
        logging.info("read volume-on bmp file")
        volume_on_bmp = Image.open(os.path.join(picdir, 'volume-on.bmp'))
        logging.info("read volume-off bmp file")
        volume_off_bmp = Image.open(os.path.join(picdir, 'volume-off.bmp'))
        logging.info("read volume-high bmp file")
        volume_high_bmp = Image.open(os.path.join(picdir, 'volume-high.bmp'))
        logging.info("read volume-low bmp file")
        volume_low_bmp = Image.open(os.path.join(picdir, 'volume-low.bmp'))
        
        # read plant status bmp files
        logging.info("read smiley face bmp file")
        smile_bmp = Image.open(os.path.join(picdir, 'smile.bmp'))
        logging.info("read water bmp file")
        water_bmp = Image.open(os.path.join(picdir, 'water.bmp'))
        
        # read stimulus bmp file
        logging.info("read lightning bmp file")
        lightning_bmp = Image.open(os.path.join(picdir, 'lightning.bmp'))        
        
        # while loop
        while True: 
            # create a new image for the welcome screen - horizontal
            welcome_image = Image.new('1', (epd.height, epd.width), 255)  # 255: white background
            draw = ImageDraw.Draw(welcome_image)
            
            # draw welcome message
            draw.text((70, 10), "Welcome to", font=font24, fill=0)
            draw.text((15, 45), "Leaf Notes", font=font50, fill=0)
            
            # draw current date and time
            now = datetime.now()
            # set timezone
            now = datetime.now(ZoneInfo("America/New_York"))
            print("Time in New York:", now.strftime("%Y-%m-%d %H:%M:%S"))
            current_time = now.strftime("%A, %B %d, %Y\n%I:%M %p")
            draw.text((10, 115), current_time, font=font20, fill=0)

            # insert logo
            resized_logo = logo_bmp.resize((90, 100))
            welcome_image.paste(resized_logo, (255, 0))
            
            # insert smiley face
            draw.text((250, 100), "Plant Status", font=font20, fill=0)
            if plant_status == 1:
                resized_smile = smile_bmp.resize((50, 50))
                welcome_image.paste(resized_smile, (280, 125))
            elif plant_status == 0:
                resized_water = water_bmp.resize((50, 50))
                welcome_image.paste(resized_water, (280, 125))

            # insert volume icons
            if os.path.exists(volume_filename):
                with open(volume_filename, "r") as f:
                    volume = f.read().strip()
            else:
                volume = "Volume: 1"
            if volume == "Volume: 0":
                volume = "Volume: OFF"
         
            if volume == "Volume: 1":
                resized_volume_low = volume_low_bmp.resize((60, 60))
                welcome_image.paste(resized_volume_low, (90, 170))  
            elif volume == "Volume: 2":
                resized_volume_on = volume_on_bmp.resize((60, 60))
                welcome_image.paste(resized_volume_on, (150, 170))				              
            elif volume == "Volume: 3":
                resized_volume_high = volume_high_bmp.resize((60, 60))
                welcome_image.paste(resized_volume_high, (210, 170))				
            elif volume == "Volume: OFF":
                resized_volume_off = volume_off_bmp.resize((60, 60))
                welcome_image.paste(resized_volume_off, (30, 170))
            
            if os.path.exists(stim_filename):
                with open(stim_filename, "r") as f:
                    stim = f.read().strip()
                    print("stim: ", stim)
            if stim == "1":
                resize_lightning = lightning_bmp.resize((60, 60))
                welcome_image.paste(resize_lightning, (270, 180))
           
            # display the image
            # epd.display(epd.getbuffer(welcome_image))
            flipped_image = welcome_image.rotate(180)
            epd.display(epd.getbuffer(flipped_image))
            # epd.lut_GC()
            epd.lut_DU() # quick refresh
            epd.refresh()
            time.sleep(0.05)
    except:
        logging.info("Clear...")
        epd.Clear()
        logging.info("ctrl + c:")
        epd3in52.epdconfig.module_exit(cleanup=True)
        exit()
    
    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in52.epdconfig.module_exit(cleanup=True)
    exit()
