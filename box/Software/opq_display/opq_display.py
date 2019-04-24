#!/usr/bin/python

"""
This module provides functions for working with the OPQ Box display module.
See: https://github.com/adafruit/Adafruit_Python_SSD1306
"""

import json
import subprocess
import time
import threading

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image, ImageDraw, ImageFont

import live_box_data


def init_display():
    """
    Initializes the display.
    """
    RST = 24  # Raspberry pi pins
    disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=1)
    disp.begin()
    return disp


class DisplayNormalThread(threading.Thread):
    def __init__(self, opq_disp):
        threading.Thread.__init__(self)
        self.opq_disp = opq_disp
        self.stopped = threading.Event()

    def sleep(self, seconds):
        cnt = 0.0
        while cnt < seconds and not self.stopped.is_set():
            time.sleep(.1)
            cnt += .1

    def run(self):
        while not self.stopped.is_set():
            self.opq_disp.display_box_info()
            self.sleep(5)
            self.opq_disp.display_system_stats(5, self.stopped)


class OpqDisplay:
    def __init__(self):
        self.disp = init_display()
        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        self.normal_display_thread = None

    def refresh(self):
        self.disp.image(self.image)
        self.disp.display()

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
            self.refresh()

    def display_system_stats(self, for_seconds, stopped):
        cnt = 0.0
        while cnt <= for_seconds and not stopped.is_set():
            self.clear_display()

            cmd = "hostname -I | cut -d\' \' -f1"
            ip = subprocess.check_output(cmd, shell=True)
            cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
            cpu = subprocess.check_output(cmd, shell=True)
            cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
            mem_usage = subprocess.check_output(cmd, shell=True)
            cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
            disk = subprocess.check_output(cmd, shell=True)

            self.draw.text((0, -2), "IP: " + str(ip), font=self.font, fill=255)
            self.draw.text((0, 6), str(cpu), font=self.font, fill=255)
            self.draw.text((0, 14), str(mem_usage), font=self.font, fill=255)
            self.draw.text((0, 23), str(disk), font=self.font, fill=255)

            self.refresh()
            cnt += .1
            self.sleep(.1)

    def display_box_metrics(self, for_seconds, stopped):
        cnt = 0.0
        url = "http://10.0.1.8:3012/push/0"
        while cnt <= for_seconds and not stopped.is_set():
            opq_box_metric = live_box_data.get_live_box_data_single(url)
            self.clear_display()
            self.draw_text("Frequency: %f" % opq_box_metric.f)
            self.draw_text("Vrms: %f" % opq_box_metric.rms)
            self.draw_text("THD: %f" % opq_box_metric.thd)
            self.refresh()
            cnt += .1
            self.sleep(.1)

    def display_ap_message(self):
        """
        Displays a message informing the user that the box is in AP mode and provides instructions on how
        to connect the box to a WiFi access point.
        """
        self.stop_normal_thread()
        self.clear_display()
        self.draw_text("OPQ Box is in AP mode")
        self.draw_text("Connect to WiFi @ OPQ", 1)
        self.draw_text("http://10.42.0.1:8888", 2)
        self.refresh()

    def display_opq_logo(self):
        """
        Displays the OPQ logo and name.
        """
        self.stop_normal_thread()
        self.clear_display()
        image = Image.open('box_display_logo.ppm').convert('1')
        self.disp.image(image)
        self.disp.display()

    def display_normal(self):
        self.stop_normal_thread()
        display_normal_thread = DisplayNormalThread(self)
        self.normal_display_thread = display_normal_thread
        display_normal_thread.start()

    def stop_normal_thread(self):
        if self.normal_display_thread is not None:
            self.normal_display_thread.stopped.set()
            self.normal_display_thread.join()
            self.normal_display_thread = None

    def clear_display(self):
        """
        Clears the display.
        """
        self.disp.clear()
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)
