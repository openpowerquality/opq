import unittest
import serial
import sys
import time

sys.path.append('../DSPutill')
import isp

#Here we test the in system programing and the UART communication.
class TestISPandUart(unittest.TestCase):
	
	def setUp(self):
		isp.init();
	#This test will check the programing via stm32flash
	def test_isp_flashing(self):
		self.assertTrue(isp.flash_dsp('testBins/uartLoopback.bin'), "Failed to program the DSP");
		#we need to wait for a bit for the DSP to reset.
		time.sleep(2);

	#This test will check the uart communication. 
	def test_Uart_loopback(self):
		#open the serial port.
		port = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=3.0)
		#write some text to the DSP.
		port.write("Aloha OPQ!");
		#read 10 characters.
		recv = port.read(10)
		#make sure what we read is what we are writen.
		self.assertEqual(recv, "Aloha OPQ!", "Failed UART communication with the DSP");
		


if __name__ == '__main__':
	#run the test.
	unittest.main()
