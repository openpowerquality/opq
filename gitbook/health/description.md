# OPQ Health

## Overview {#overview}

With OPQ having so many different services running at the same time, it can be difficult to keep track of whether or not each individual service is consistently and properly running. OPQ Health is a monitoring service that detects the 'health' of OPQ's core services in real-time. The health of a running OPQ service is determined by the services ability to properly run. For example, if an OPQ box is to be considered healthy, it must be consistently publishing new power quality events.
* OPQ Boxes - Detect if new events are consistently being published
* OPQ Mauka -
* OPQ View -
* Mongo - Detect if OPQ's mongo collections are running and being updated


### Installation {#installation}

The health service is run with python 3. Simply cd into the opq/health directory and run python3 health.py to start the service.

### Data Model {#data-model}

Mock mongo schema
```
db.createCollection("health", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: [ "service", "up", "start", "end", "specify"],
         properties: {
            service: {
               enum: [ "BOX", "MAUKA", "VIEW", "MONGO"],
               description: "Identifies the service the event is for"
            },
            up: {
               bsonType: "bool",
               description: "True if uptime, False if downtime"
            },
            start: {
               bsonType: "long",
               description: "Start of uptime/downtime interval"
            },
            emd: {
               bsonType: "long",
               description: "End of uptime/downtime interval"
            },
            specify: {
               bsonType: "string",
               description: "Additional identifier. i.e. can be used to identify box number"
            }
         }
      }
   }
})
```

### Analytics {#analytics}

Notifications for "unhealthy" services. Data visualization for each service?
