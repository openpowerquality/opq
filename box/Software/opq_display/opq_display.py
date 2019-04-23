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


def init_display():
    """
    Initializes the display.
    """
    RST = 24  # Raspberry pi pins
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=1)
    disp.begin()
    return disp


class OpqDisplay:
    def __init__(self):
        self.disp = init_display()
        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

    def sleep(self, seconds):
        time.sleep(seconds)

    def draw_text(self, text, line=0, x=0):
        y = line * 8
        self.draw.text((x, y), text, font=self.font, fill=255)

    def display_box_info(self):
        with open("/etc/opq/opqbox_config.json") as json_in:
            self.clear_display()
            opqbox_config = json.load(json_in)
            self.draw_text("OPQ Box Information")
            self.draw_text("Box ID: %d" % opqbox_config["box_id"], 1)
            self.draw_text("Calib.: %f" % opqbox_config["calibration"], 2)
            self.disp.image(self.image)
            self.disp.display()

    def display_ap_message(self):
        """
        Displays a message informing the user that the box is in AP mode and provides instructions on how
        to connect the box to a WiFi access point.
        """
        self.clear_display()
        self.draw_text("OPQ Box is in AP mode")
        self.draw_text("Connect to WiFi @ OPQ", 1)
        self.draw_text("http://10.42.0.1:8888", 2)
        self.disp.image(self.image)
        self.disp.display()

    def display_opq_logo(self):
        """
        Displays the OPQ logo and name.
        """
        self.clear_display()
        image = Image.open('box_display_logo.ppm').convert('1')
        self.disp.image(image)
        self.disp.display()

    def clear_display(self):
        """
        Clears the display.
        """
        self.disp.clear()
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)
