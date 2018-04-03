EESchema Schematic File Version 2
LIBS:opqbox3
LIBS:device
LIBS:power
LIBS:conn
LIBS:opqbox3-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 4 5
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text HLabel 7000 4100 2    60   Output ~ 0
SPI_MOSI
Text HLabel 7000 4000 2    60   Input ~ 0
SPI_MISO
Text HLabel 7000 3900 2    60   Output ~ 0
SPI_nCS
Text HLabel 7000 4200 2    60   Output ~ 0
SPI_nCLK
Text HLabel 7000 4700 2    60   Output ~ 0
UART_TX
Text HLabel 7000 4800 2    60   Input ~ 0
UART_RX
$Comp
L GND #PWR033
U 1 1 5A9AD0C2
P 6050 5400
F 0 "#PWR033" H 6050 5150 50  0001 C CNN
F 1 "GND" H 6050 5250 50  0000 C CNN
F 2 "" H 6050 5400 50  0001 C CNN
F 3 "" H 6050 5400 50  0001 C CNN
	1    6050 5400
	1    0    0    -1  
$EndComp
Text HLabel 5200 4000 0    60   Output ~ 0
BOOT_MODE
Text HLabel 5200 3500 0    60   BiDi ~ 0
FLAG1
Text HLabel 5200 4100 0    60   Output ~ 0
JTAG_nRST
$Comp
L +5V #PWR034
U 1 1 5A9B4CD7
P 5950 2600
F 0 "#PWR034" H 5950 2450 50  0001 C CNN
F 1 "+5V" H 5950 2740 50  0000 C CNN
F 2 "" H 5950 2600 50  0001 C CNN
F 3 "" H 5950 2600 50  0001 C CNN
	1    5950 2600
	1    0    0    -1  
$EndComp
$Comp
L Raspberry_Pi_2_3 J3
U 1 1 5AC2C93D
P 6100 4000
F 0 "J3" H 6800 2750 50  0000 C CNN
F 1 "Raspberry_Pi_2_3" H 5700 4900 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_2x20" H 7100 5250 50  0001 C CNN
F 3 "" H 6150 3850 50  0001 C CNN
	1    6100 4000
	1    0    0    -1  
$EndComp
Wire Wire Line
	5900 2700 5900 2650
Wire Wire Line
	5900 2650 6000 2650
Wire Wire Line
	5950 2650 5950 2600
Wire Wire Line
	6000 2650 6000 2700
Connection ~ 5950 2650
Wire Wire Line
	5700 5300 5700 5350
Wire Wire Line
	5700 5350 6400 5350
Wire Wire Line
	6050 5350 6050 5400
Wire Wire Line
	6400 5350 6400 5300
Connection ~ 6050 5350
Wire Wire Line
	5800 5300 5800 5350
Connection ~ 5800 5350
Wire Wire Line
	5900 5300 5900 5350
Connection ~ 5900 5350
Wire Wire Line
	6000 5300 6000 5350
Connection ~ 6000 5350
Wire Wire Line
	6100 5300 6100 5350
Connection ~ 6100 5350
Wire Wire Line
	6200 5300 6200 5350
Connection ~ 6200 5350
Wire Wire Line
	6300 5300 6300 5350
Connection ~ 6300 5350
NoConn ~ 5200 3300
NoConn ~ 5200 3400
NoConn ~ 5200 3600
NoConn ~ 5200 3700
NoConn ~ 5200 3800
NoConn ~ 5200 3900
NoConn ~ 5200 4200
NoConn ~ 5200 4300
NoConn ~ 5200 4400
NoConn ~ 5200 4700
NoConn ~ 5200 4800
NoConn ~ 7000 4400
NoConn ~ 7000 4500
NoConn ~ 7000 3800
NoConn ~ 7000 3600
NoConn ~ 7000 3500
NoConn ~ 7000 3300
NoConn ~ 7000 3200
NoConn ~ 7000 3100
NoConn ~ 6200 2700
NoConn ~ 6300 2700
$EndSCHEMATC
