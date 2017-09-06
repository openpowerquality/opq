import RPi.GPIO as GPIO
from time import sleep
from subprocess import call


def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    # Setup bootmode
    GPIO.setup(23, GPIO.OUT)
    # Setup \reset
    GPIO.setup(24, GPIO.OUT)


def reset_dsp():
    # Set the DSP to boot from flash.
    GPIO.output(23, False)
    # Bang on the reset.
    GPIO.output(24, False)
    sleep(0.1)
    GPIO.output(24, True)

def bootloader_dsp():
    # Set the DSP to enter serial bootloader.
    GPIO.output(23, True)
    # Bang on the reset.
    GPIO.output(24, False)
    sleep(0.1)
    GPIO.output(24, True)


def flash_dsp(fname):
    bootloader_dsp();
    sleep(0.5);
    GPIO.output(23, False)
    if (call(["stm32flash", "-w", fname, "-v", "/dev/ttyAMA0", "-g", "0x0"])):
        return False
    reset_dsp()
    return True


if __name__ == "__main__":
    init()
    flash_dsp('opq.bin')
