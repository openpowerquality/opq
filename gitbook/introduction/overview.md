# OPQ System Overview

## Description {#description}
The OPQ system consists of open source hardware and software components that provide end-to-end support for the capture, triggering, analysis, and reporting of consumer level local and global PQ events.

### Components
**Box** is an open source hardware platform for capturing and transferring PQ events to our cloud services.

**Makai** is a cloud based middleware responsible for analyzing low fidelity data in order to request bandwidth limited high fidelity data from boxes for further analysis.

**Mauka** is a cloud based middleware responsible for higher-level analytics of PQ data. Mauka provides various algorithms for classifying PQ events.  

**View** is a cloud based web server and visualization platform which provides reporting of PQ events collected by the other OPQ System components.

**Protocol** provides a data serialization standard that is used to provide internal and external communication between the various APIs of the OPQ system components.

**Misc. Utilities** are provided in the form of shell and Python scripts and perform tasks such as installation, documentation generation, signing/variation, key generation, etc.

### Data Flow
1. Power data is collected on Boxes
2. Boxes perform feature extraction locally, and send low fidelity data to Makai
3. Makai analyzes the low fidelity feature extracted data for interesting features
4. When interesting features are found, Makai requests appropriate Boxes for raw data
5. Requested Boxes send raw data back to Makai, where it is stored in a Mongo database
6. Mauka utilizes the stored data to perform classification of PQ events and determine if PQ events are local or globally distributed
7. Classification products/results are stored back to a Mongo database where they are interpreted and visualized by View 

![https://raw.githubusercontent.com/openpowerquality/ieee-cyber-2017/master/paper-presentation/resources/system-diagram.png](https://raw.githubusercontent.com/openpowerquality/ieee-cyber-2017/master/paper-presentation/resources/system-diagram.png)

## Features {#features}
OPQ system features organized by component.

##### Box
* Capture sampled power waveform
* Local feature extraction
* Data is transferred securely to our cloud services via user's WiFi
* Optional GPS synchronization
* Optional battery backup

##### Makai
* Analyze low fidelity feature extracted PQ data received from Boxes
* Trigger appropriate Boxes for raw data for further analysis
* Scalable plugin based architecture

##### Mauka
* Classification of PQ events
* Localization of PQ events
* Storage and analysis of long term PQ trends
* Scalable plugin based architecture

##### View
* Public display and visualization of local and global PQ events
* Per user management of Boxes, preferences, and personal data
* *Expert mode* for access to raw data and more advanced analytics/reports

##### Protocol
* Provides a serialization standard between OPQ system components
* Utilizes Google's Protocol Buffers https://developers.google.com/protocol-buffers/ which provides a programming language agnostic way of (de)serializing data

## Roadmap {#roadmap}
