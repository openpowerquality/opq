# OPQMauka

## Overview {#overview}

OPQMauka is a distributed plugin-based middleware for OPQ that provides higher level analytic capabilities. OPQMauka provides analytics for classification of PQ events, aggregation of triggering data for long term trend analysis, community detection, statistics, and metadata management.  

### Software {#software}
OPQMauka is written in Python 3 and depends on 2 ZMQ brokers as well as a Mongo database. The architecture of OPQMauka is designed in such a way that all analytics are provided by plugins that communicate using publish/subscribe semantics using ZMQ. This allows for a distributed architecture and horizontal scalability. 

The OPQMauka processing pipeline is implemented as a directed acyclic graph (DAG). Communication between vertexes in the graph is provided via ZeroMQ. Each node in the graph is implemented by an OPQMauka Plugin. Additional analysis plugins can be added to OPQMauka at runtime, without service interruption.

Each OPQMauka Plugin provides a set of topics that it subscribes to and a set of topics that it produces. These topics form the edges between vertexes in our graph. Because each plugin is independent and only relies on retrieving and transmitting data over ZeroMQ, plugins can be implemented in any programming language and executed on any machine in a network. This design allows us to easily scale plugins across multiple machines in order to increase throughput.

### Use Cases {#use-cases}

* Recording long term trends from triggering measurements
* Classification of voltage dip/swells
* Classification of frequency dip/swells
* Requests of raw data for higher level analytics, including:
  * Community detection
  * Grid topology
  * Global/local event detection/discrimination
  * Integration with other data sources (_i.e._ PV production)

