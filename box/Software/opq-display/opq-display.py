#!/usr/bin/python

"""
This module provides functions for working with the OPQ Box display module.
See: https://github.com/adafruit/Adafruit_Python_SSD1306
"""

import json
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image, ImageDraw, ImageFont



def draw_text(draw, font, text, line=0, x=0):
    y = line * 8
    draw.text((x, y), text, font=font, fill=255)

def display_box_info(disp, draw, image, font):
    with open("/etc/opq/opqbox_config.json") as json_in:
        opqbox_config = json.load(json_in)
        draw_text(draw, font, "OPQ Box Information")
        draw_text(draw, font, "Box ID: %d" % opqbox_config["box_id"], 1) 
        draw_text(draw, font, "Calib.: %f" % opqbox_config["calibration"], 2)
        disp.image(image)
        disp.display()

def display_ap_message(disp, draw, image, font):
    """
    Displays a message informing the user that the box is in AP mode and provides instructions on how
    to connect the box to a WiFi access point.
    """
    draw_text(draw, font, "OPQ Box is in AP mode")
    draw_text(draw, font, "Connect to WiFi @ OPQ", 1)
    draw_text(draw, font, "http://10.42.0.1:8888", 2)
    disp.image(image)
    disp.display()

def display_opq_logo(disp):
    """
    Displays the OPQ logo and name.
    """
    image = Image.open('box_display_logo.ppm').convert('1')
    disp.image(image)
    disp.display()

def clear_display(disp, draw):
    """
    Clears the display.
    """
    disp.clear()
    draw.rectangle((0,0, disp.width, disp.height), outline=0, fill=0)


def init_display():
    """
    Initializes the display.
    """
    RST = 24 # Raspberry pi pins
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=1)
    disp.begin()
    return disp

if __name__ == "__main__":
    disp = init_display()
    image = Image.new('1', (disp.width, disp.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    clear_display(disp, draw) 
    display_opq_logo(disp)

    time.sleep(1)

    clear_display(disp, draw)
    display_ap_message(disp, draw, image, font)

    time.sleep(1)
    clear_display(disp, draw)
    display_box_info(disp, draw, image, font)
