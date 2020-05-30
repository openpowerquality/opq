# Overview

The mission of the Open Power Quality project is to design and implement open source hardware, software, and data for low cost, crowd-sourced power quality monitoring, storage, and analysis. For more details, please see our [home page](http://openpowerquality.org).

This repository provides the schematics for the second generation Open Power Quality metering device (OPQBox2). 
  
# PSU Design
Main power for the board is provided by the IRM-10-5 module. Hot side is powered via ADUM5010 chipscale isolated DC-DC converter.

![ADUM5010 PSU design](https://raw.githubusercontent.com/openpowerquality/box/master/images/power-isolation.png)

Design notes:
  * 2A of power on the isolated side
  * 0.22uF super capacitor.(~1s interruption protection)
  * 250mW of power on the HOT side.
  * 
# Measurement isolation design

![capacitive PSU](https://raw.githubusercontent.com/openpowerquality/box/master/images/measurement-isolation.png)

Design notes:

  * Measurement is isolated via an isolation amplifier: [TI AMC 1100](http://www.ti.com/product/amc1100).
  * 16bit, 100 kSPS differential ADC: [Analog Devices AD7684](http://www.analog.com/en/analog-to-digital-converters/ad-converters/ad7684/products/product.html).
  * Flame proof, pulse withstanding resistors for voltage measurement.
  * Thermal metal oxide varistors for surge protection: 

# Layout

PCB layout is available in the schematics folder. It is provided as a PADs Layout file, as well as gerbers and pdf/image files. This design calls for a 4 layer FR4 board, and measures 100mm by 100mm.  PCB is manufactued and is undergoing testing. This device is intended as an engineering sample. We expect to go through several iterations refining the design. 

### Top copper, soldermask, and silkscreen


![layout](https://github.com/openpowerquality/opq/blob/master/box/images/layout_top.png)

### Bottom copper, soldermask and silkscreen

![layout](https://github.com/openpowerquality/opq/blob/master/box/images/layout_bottom.png)

# Safety

We have domain knowledge in measurement/DSP, but not PSU design and consumer products. From a safety perspective, we have implemented the following:

  * Creepage/Clearance appropriate for mains power.
  * Isolated power and sensing for all user serviceable components.
  * Circuit Protection (MOV, TVC, etc).
  * EMI, fuse, component rating... etc.

# Engineering sample

We recently produced an engineering sample of this design:

![](https://github.com/openpowerquality/opq/blob/master/box/images/opqbox_pcb.jpg)



# Additional design documents

 
  * [OPQBOX2 pdf schematic](https://github.com/openpowerquality/box/blob/master/Schematics/opqbox2_schematic.pdf?raw=true)
  * [Bill of Materials](https://raw.githubusercontent.com/openpowerquality/box/master/Schematics/BOM.txt)
  * [Mentor graphics PADS schematic of OPQBOX2](https://github.com/openpowerquality/box/blob/master/Schematics/opqbox2.sch?raw=true)
  * [PADS library](https://github.com/openpowerquality/box/tree/master/Schematics/Library)
  
# Changes From OPQBox Version 1

OPQBox2 is a complete redesign from the previous generation. It replaces the voltage sensing transformer with an isolation amplifier. The sampling rate has increased from 4kSPS to up to 100kSPS. In order to keep up with the faster acquisition a dedicated ARM DSP is used to control the sampling and realtime processing. Here is a summary of component changes in OPQBox2:

 
|                | OPQBox1 | OPQBox2|
|--------------- | ------- | -------|
|**Voltage sensing/Isolation** | 12V transformer wall plug transformer | Isolation amplifier.|
|**Power**       | 12V transformer | Isolated 5V AC-DC,  Isolated 5V DC-DC |
|**ADC**         | 4KSPS 16Bit ADC | 100 KSPS 16Bit ADC |
|**Processing**  | Raspberry Pi for processing/WiFi | Dedicated ARM DSP for real time processing. |
|                |         | Raspberry PI for communication and configuration only. |
|                |         | PI can be replaced with CAN/RF/Ethernet/GSM module |


  
