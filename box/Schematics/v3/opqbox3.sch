EESchema Schematic File Version 2
LIBS:opqbox3
LIBS:device
LIBS:power
LIBS:conn
LIBS:contrib
LIBS:stm32
LIBS:opqbox3-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 3
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 2150 1200 1550 1600
U 5A829EE9
F0 "power" 60
F1 "power.sch" 60
F2 "LINE" I L 2150 1500 60 
F3 "NEUTRAL" I L 2150 1950 60 
F4 "+3.3V" O R 3700 2500 60 
F5 "+5V" O R 3700 2350 60 
F6 "GND" O R 3700 2650 60 
F7 "3.3VREF" O R 3700 1950 60 
F8 "ADC" O R 3700 1350 60 
$EndSheet
Wire Notes Line
	2900 500  2900 7750
$Comp
L Conn_01x02_Male J1
U 1 1 5A82EE79
P 1450 1400
F 0 "J1" H 1450 1500 50  0000 C CNN
F 1 "Conn_01x02_Male" H 1450 1200 50  0000 C CNN
F 2 "" H 1450 1400 50  0001 C CNN
F 3 "" H 1450 1400 50  0001 C CNN
	1    1450 1400
	1    0    0    -1  
$EndComp
$Comp
L Conn_01x02_Male J2
U 1 1 5A82EEC2
P 1450 1950
F 0 "J2" H 1450 2050 50  0000 C CNN
F 1 "Conn_01x02_Male" H 1450 1750 50  0000 C CNN
F 2 "" H 1450 1950 50  0001 C CNN
F 3 "" H 1450 1950 50  0001 C CNN
	1    1450 1950
	1    0    0    -1  
$EndComp
Wire Wire Line
	1650 1400 1700 1400
Wire Wire Line
	1700 1400 1700 1500
Wire Wire Line
	1650 1500 2150 1500
Connection ~ 1700 1500
Wire Wire Line
	1650 2050 1700 2050
Wire Wire Line
	1700 2050 1700 1950
Wire Wire Line
	1650 1950 2150 1950
Connection ~ 1700 1950
$Comp
L PWR_FLAG #FLG01
U 1 1 5A82F319
P 1900 1450
F 0 "#FLG01" H 1900 1525 50  0001 C CNN
F 1 "PWR_FLAG" H 1900 1600 50  0000 C CNN
F 2 "" H 1900 1450 50  0001 C CNN
F 3 "" H 1900 1450 50  0001 C CNN
	1    1900 1450
	1    0    0    -1  
$EndComp
$Comp
L PWR_FLAG #FLG02
U 1 1 5A82F35B
P 1900 1900
F 0 "#FLG02" H 1900 1975 50  0001 C CNN
F 1 "PWR_FLAG" H 1900 2050 50  0000 C CNN
F 2 "" H 1900 1900 50  0001 C CNN
F 3 "" H 1900 1900 50  0001 C CNN
	1    1900 1900
	1    0    0    -1  
$EndComp
Wire Wire Line
	1900 1900 1900 1950
Connection ~ 1900 1950
Wire Wire Line
	1900 1450 1900 1500
Connection ~ 1900 1500
Text Notes 3050 3150 0    60   ~ 0
Isolated
Text Notes 2150 3150 0    60   ~ 0
NOT isolated
$Sheet
S 4300 1200 1600 1600
U 5A835DDE
F0 "dsp" 60
F1 "dsp.sch" 60
F2 "3.3VREF" I L 4300 1950 60 
F3 "SPI" B R 5900 1650 60 
F4 "JTAG" B R 5900 1800 60 
F5 "UART" B R 5900 2000 60 
F6 "PPS" O R 5900 2600 60 
F7 "LED" O R 5900 2450 60 
F8 "BOOT_MODE" I L 4300 2600 60 
F9 "VBAT" I L 4300 2400 60 
F10 "FLAG1" B R 5900 2250 60 
F11 "ADC" I L 4300 1350 60 
$EndSheet
Wire Wire Line
	3700 1950 4300 1950
Wire Bus Line
	3700 1350 4300 1350
$EndSCHEMATC
