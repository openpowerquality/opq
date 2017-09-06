# Overview

The mission of the Open Power Quality project is to design and implement open source hardware, software, and data for low cost, crowd-sourced power quality monitoring, storage, and analysis. For more details, please see our [home page](http://openpowerquality.org).

This repository provides the proposed schematics for the second generation Open Power Quality metering device (OPQBox2). 

OPQBox2 is in the final design stage.  We are circulating this design to solicit feedback and make improvements prior to production. We greatly appreciate your willingness to provide us with feedback.

# Goal

The goal of OPQBox is to monitor voltage and frequency and detect departures from nominal levels.  It accomplishes this by sampling the waveform 256 times per cycle, extracting power quality measures (including frequency, RMS voltage, and THD), and then uploading data about these measures to the OPQHub service. 

OPQBox can be configured to send a "heartbeat" message to OPQHub to indicate that it is connected and functioning. This message normally includes low resolution voltage and frequency data.   

When a power quality disturbance is detected by OPQBox, it sends a message to OPQHub that includes high resolution voltage and frequency data. 

We plan for OPQBox timestamp data to be synchronized to within 1 millisecond, though we are currently experimenting to determine the best technique to accomplish this. Synchronization enables data from multiple OPQBoxes to be used to generate a global perspective on the state of the grid.  As a simple example, it can enable users to determine if their event is local to their own residence or instead grid-wide. 

# Operational requirements

The design of OPQBox2 is influenced by our experience with the first generation OPQBox (OPQBox1).  Design information about our first generation hardware is available at the [OPQBox1 repository](https://github.com/openpowerquality/opqbox1). 

We performed a [pilot study of our first generation hardware and software](http://openpowerquality.org/technology/g1-pilot-study.html), and one of the results of this study are the following major enhancements for OPQBox2:

 * **Safety.**  OPQBox2 is meant to bypass power filters and surge protectors. Thus it incorporates extra protection elements to keep the device operating safely during power disruptions. Fuses will disable OPQBox2 in case of a fault. All of the user accesible components are isolated from the mains power.

 * **Satisfy IEEE PQ standards.**  OPQBox2 can be plugged into a standard U.S. two prong outlet with expected power at a frequency of 60 Hz and with a voltage of 120 V. It can operate under a frequency range of 50 Hz to 70 Hz and under a voltage range of 80 Vac to 400 Vac. Sampling is phase locked to the utility frequency. The 16 bit 100KSPS ADC allows for 5mV resolution with over 1024 points per grid cycle. On board ARM floating point DSP is able to perform the IEEE 1159 outlined analysis, as well as user defined code.

 * **Support event recording upon power failure.** OPQBox2 adds a super capacitor circuit designed to provide power during service interuptions. 

* **Connectivity.** OPQBox2 is designed to be the deployed as a part of a distributed real-time power quality monitoring network. As such it offers a large number of interface options, including serial, USB, WIFI and cellular network. The initial development will focus on WIFI, and serial communication.
  
# Changes From OPQBox Version 1

OPQBox2 is a complete redesign from the previous generation. It replaces the voltage sensing transformer with an isolation amplifier. The sampling rate has increased from 4kSPS to up to 100kSPS. In order to keep up with the faster acquisition a dedicated ARM DSP is used to control the sampling and realtime processing. Here is a summary of component changes in OPQBox2:

 
                | OPQBox1 | OPQBox2
--------------- | ------- | -------
**Voltage sensing/Isolation** | 12V transformer wall plug transformer | Isolation amplifier.
**Power**       | 12V transformer | Isolated 5V AC-DC,  Isolated 5V DC-DC
**ADC**         | 4KSPS 16Bit ADC | 100 KSPS 16Bit ADC
**Processing**  | Raspberry Pi for processing/WiFi | Dedicated ARM DSP for real time processing.
                |         | Raspberry PI for communication and configuration only.
                |         | PI can be replaced with CAN/RF/Ethernet/GSM module


# PSU Design
Main power for the board is provided by the IRM-10-5 module. Hot side is powered via ADUM5010 chipscale isolated DC-DC converter.

![ADUM5010 PSU design](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/power-isolation.png)

Design notes:
  * 2A of power on the isolated side
  * 0.22uF super capacitor.(~1s interruption protection)
  * 250mW of power on the HOT side.
  * 
# Measurement isolation design

![capacitive PSU](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/measurement-isolation.png)

Design notes:

  * Measurement is isolated via an isolation amplifier: [TI AMC 1100](http://www.ti.com/product/amc1100).
  * 16bit, 100 kSPS differential ADC: [Analog Devices AD7684](http://www.analog.com/en/analog-to-digital-converters/ad-converters/ad7684/products/product.html).
  * Flame proof, pulse withstanding resistors for voltage measurement.
  * Thermal metal oxide varistors for surge protection: 

# Layout

PCB layout is available in the schematics folder. It is provided as a PADs Layout file, as well as gerbers and pdf/image files. This design calls for a 4 layer FR4 board, and measures 100mm by 100mm.  PCB is manufactued and is undergoing testing. This device is intended as an engineering sample. We expect to go through several iterations refining the design. 

### Full Layout


![layout](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/opqbox2,5full.png)

The Isolation barrier is clearly visible. Perhaps a cutout is appropriate to improve isolation?

### Top copper, soldermask, and silkscreen


![layout](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/opqbox2.5Top.png)

### Bottom copper, soldermask and silkscreen

![layout](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/opqbox2.5Bottom.png)

# Safety

We have domain knowledge in measurement/DSP, but not PSU design and consumer products. From a safety perspective, we have implemented the following:

  * Creepage/Clearance appropriate for mains power.
  * Isolated power and sensing for all user serviceable components.
  * Circuit Protection (MOV, TVC, etc).
  * EMI, fuse, component rating... etc.

# Engineering sample

We recently produced an engineering sample of this design:

![](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/images/opqbox2-engineering-sample.JPG)

# Additional design documents

 
  * [OPQBOX2 pdf schematic](https://github.com/openpowerquality/opqbox2/blob/master/Schematics/opqbox2_schematic.pdf?raw=true)
  * [Bill of Materials](https://raw.githubusercontent.com/openpowerquality/opqbox2/master/Schematics/BOM.txt)
  * [Mentor graphics PADS schematic of OPQBOX2](https://github.com/openpowerquality/opqbox2/blob/master/Schematics/opqbox2.sch?raw=true)
  * [PADS library](https://github.com/openpowerquality/opqbox2/tree/master/Schematics/Library)
  


# Summary of questions for review

Here are the issues we are most concerned about.

  * Should we use a cut-out to improve isolation? 
  * Do you have any other recommendations to improve safety?
  * Do you have any other recommendations to improve measurement accuracy, precision, or reliability?
  * Do you have any recommendations for certifications? (UL, IEEE, IEC, etc)
  
If you would like to meet in person or via teleconference to discuss this design, we would be happy to arrange that. If you can reply with comments to johnson@hawaii.edu, that would be great. 

Thanks so much for your time!  
