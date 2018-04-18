## Introduction

* [Why Open Power Quality?](README.md)
* [About Power Quality](introduction/power-quality.md)
  * [What is Power Quality?](introduction/power-quality.md#what)
  * [Why Care About Power Quality?](introduction/power-quality.md#why)
  * [Types of Power Quality Issues](introduction/power-quality.md#issues)
  * [How Distributed Renewables Affect Power Quality](introduction/power-quality.md#renewables)
* [OPQ System Overview](introduction/overview.md)
  
## Installation

* [Prerequisites](installation-prerequisites.md)
* [OPQ Box](box/installation.md)
* [OPQ View](view/installation.md)
* [OPQ Mauka](mauka/installation.md)
* [OPQ Makai](makai/installation.md)
* [OPQ Protocol](protocol/installation.md)

## Developer Guide
* [GitBook](developerguide/gitbook.md)
* [MongoDB](developerguide/mongodb.md)
* [Deployment](developerguide/deployment/deploy-overview.md)
  * [Configure host](developerguide/deployment/deploy-configure-host.md)
  * [View](developerguide/deployment/deploy-view.md)
  * [Mauka](developerguide/deployment/deploy-mauka.md)
  * [Makai](developerguide/deployment/deploy-makai.md)
  * [Health](developerguide/deployment/deploy-health.md)


## OPQ Box

* [Design](box/description.md)
  * [Hardware components](box/description.md#hardware)
  * [Software components](box/description.md#software)
  * [Frequency calculation](box/description.md#frequency)
  * [Voltage calculation](box/description.md#voltage)
  * [Data transmission](box/description.md#transmission)
  * [Synchronization](box/description.md#synchronization)
* [Manufacturing](box/manufacturing.md)
* [Firmware doxygen](https://open-power-quality.gitbooks.io/open-power-quality-manual/content/box/firmware/)
* [Triggering doxygen](https://open-power-quality.gitbooks.io/open-power-quality-manual/content/box/triggering/)


## OPQ View

* [Installation](view/installation.md)
  * [Install Meteor](view/installation.md#install-meteor)
  * [Install Libraries](view/installation.md#install-libraries)
  * [Configure settings](view/installation.md#configure-settings)
  * [Snapshot DB](view/installation.md#use-snapshot)
  * [Production DB](view/installation.md#use-production)
  * [Run OPQView](view/installation.md#run-opqview)
* [Coding Standards](view/codingstandards.md)
* [User Guide](view/userguide.md)

## OPQ Mauka

* [Overview](mauka/description.md#overview)
* [Software](mauka/description.md#software)
* [Use Cases](mauka/description.md#use-cases)
* [Plugins](mauka/plugins.md)
  * [Base Plugin](mauka/plugins.md#base)
  * [Measurement Plugin](mauka/plugins.md#measurement)
  * [Threshold Plugin](mauka/plugins.md#threshold)
  * [Frequency Threshold Plugin](mauka/plugins.md#frequency)
  * [Voltage Threshold Plugin](mauka/plugins.md#voltage)
  * [Acquisition Trigger Plugin](mauka/plugins.md#acuiqisition)
  * [Total Harmonic Distortion Plugin](mauka/plugins.md#thd)
  * [ITIC Plugin](mauka/plugins.md#itic)
  * [Status Plugin](mauka/plugins.md#status)
  * [Print Plugin](mauka/plugins.md#print)
  * [Plugin Development](mauka/plugins.md#development)
* [Message Injection]()
* [APIs](mauka/apis.md)

## OPQ Makai

* [Overview](makai/description.md#overview)
* [Software](makai/description.md#software)
* [Use Cases](makai/description.md#use-cases)
* [Makai Docs](makai/doc/makai/index.html)

## OPQ Health

* [Overview](health/description.md#overview)
* [Data Model](health/description.md#data-model)
* [Basic Operation](health/description.md#basic-operation)
* [Installation](health/description.md#installation)
* [Analytics](health/description.md#analytics)


## OPQ Protocol

* [Overview](protocol/description.md)

## OPQ Data Model

* [Overview](datamodel/description.md#overview)
* [Measurements](datamodel/description.md#measurements)
* [Trends](datamodel/description.md#trends)
* [Events](datamodel/description.md#events)
* [Box_Events](datamodel/description.md#box_events)
* [GridFS](datamodel/description.md#gridfs)
* [Locations](datamodel/description.md#locations)
* [Regions](datamodel/description.md#regions)
* [OPQ_Boxes](datamodel/description.md#opq_boxes)
* [Users](datamodel/description.md#users)

## OPQ VM/Sim

* [Overview](vm/vm.md#overview)
* [Installation](vm/vm.md#installtion)
* [Running](vm/vm.md#running)
* [Interacting w/ VM](vm/interactingvm)
* [Simulator](vm/interactingsim)

