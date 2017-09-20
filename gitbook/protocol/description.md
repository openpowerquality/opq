# OPQ Protocol

## Overview {#overview}

Data and messages passed between components of the OPQ framework are serialized and standardized using version 2 of Google's Protocol Buffers (protobuf) library [https://developers.google.com/protocol-buffers/](https://developers.google.com/protocol-buffers/).

The OPQ Protocol is currently utilized by OPQBox, OPQMakai, and OPQMauka for data serialization between services. The OPQBox sends both raw data and triggering messages encoded with protobuf. Data requests from OPQMakai to OPQBox are serialized via protobuf. Data requests from OPQMauka to OPQMakai are are serialized using protobuf. 

The fully documented OPQ Protocol definition can be found at [https://github.com/openpowerquality/opq/blob/master/protocol/opq.proto](https://github.com/openpowerquality/opq/blob/master/protocol/opq.proto).


