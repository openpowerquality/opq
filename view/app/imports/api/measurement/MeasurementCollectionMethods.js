import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Measurements } from './MeasurementCollection.js';
import { BoxEvents } from '../boxEvent/BoxEventCollection.js';

export const getActiveDeviceIdsVM = new ValidatedMethod({
  name: 'Measurements.getActiveDeviceIds',
  validate: new SimpleSchema({
    startTimeMs: {type: Number}
  }).validator({clean: true}),
  run({ startTimeMs }) {
    const recentMeasurements = Measurements.find({timestamp_ms: {$gte: startTimeMs}}, {fields: {device_id: 1}}).fetch();

    // Returns an array of unique deviceIds, sorted asc.
    return (recentMeasurements.length > 0) ? _.uniq(_.pluck(recentMeasurements, 'device_id')).sort((a, b) => a - b) : null;
  }
});

export const getEventMeasurements = new ValidatedMethod({
  name: 'Measurements.getEventMeasurements',
  validate: new SimpleSchema({
    boxEvent_id: {type: Mongo.ObjectID}
  }).validator({clean: true}),
  run({ boxEvent_id }) {
    if (!this.isSimulation) {
      // Task is to figure out time range of data to retrieve. BoxEvents with a 'reqId' indicate the start of a new
      // event. BoxEvents without a 'reqId' field are considered deadzone events, which we can consider as a continuation
      // of the most recent BoxEvent with a reqId field.
      const event = BoxEvents.findOne({_id: boxEvent_id});

      // Case 1: BoxEvent has reqId. Grab that event plus all following events without a reqId until we hit a new event
      // with another reqId, indicating a different event.
      const nextEventWithReqId = BoxEvents.findOne({
        eventEnd: {$gte: event.eventEnd},
        _id: {$ne: event._id},
        reqId: {$exists: true},
        deviceId: event.deviceId
      }, {
        sort: {eventEnd: 1}
      });

      const lastDeadzoneEvent = BoxEvents.findOne({
        deviceId: event.deviceId,
        eventEnd: {
          $gte: event.eventEnd,
          $lte: (nextEventWithReqId) ? nextEventWithReqId.eventEnd : new Date()
        },
        _id: {$nin: [event._id, (nextEventWithReqId) ? nextEventWithReqId._id : null]},
        reqId: {$exists: false}
      }, {
        sort: {eventEnd: -1}
      });

      const eventTimestampRange = {
        startTime: event.eventStart,
        endTime: (lastDeadzoneEvent) ? lastDeadzoneEvent.eventEnd : event.eventEnd // Handles case where given event is coincidentally the last deadzone event.
      };

      // Case 2: Given BoxEvent has no reqId. Look backwards until we find the initial triggering event with a reqId.
      if (!event.reqId) {
        // Find the initial triggering event, since current event is a deadzone event.
        const initialEvent = BoxEvents.findOne({
          eventEnd: {$lte: event.eventEnd},
          _id: {$ne: event._id},
          reqId: {$exists: true},
          deviceId: event.deviceId
        }, {
          sort: {eventEnd: -1}
        });

        eventTimestampRange.startTime = initialEvent.eventStart;
      }

      const eventMeasurements = Measurements.find({
        device_id: event.deviceId,
        timestamp_ms: {$gte: eventTimestampRange.startTime.getTime(), $lte: eventTimestampRange.endTime.getTime()}
      }, {
        sort: {eventEnd: 1}
      }).fetch();

      const firstMeasurementTimestamp = eventMeasurements[0].timestamp_ms;
      const lastMeasurementTimestamp = eventMeasurements[eventMeasurements.length - 1].timestamp_ms;

      // Let's also retrieve some measurements preceding and proceeding event range. 20% of event range on both sides.
      const eventDurationMs = (eventTimestampRange.endTime.getTime() - eventTimestampRange.startTime.getTime());
      const precedingTimestamp = eventTimestampRange.startTime.getTime() - (eventDurationMs * 0.2);
      const proceedingTimestamp = eventTimestampRange.endTime.getTime() + (eventDurationMs * 0.2);

      const precedingMeasurements = Measurements.find({
        device_id: event.deviceId,
        // timestamp_ms: {$gte: precedingTimestamp, $lte: eventTimestampRange.startTime.getTime()}
        timestamp_ms: {$gte: precedingTimestamp, $lte: firstMeasurementTimestamp}
      }, {}).fetch();

      const proceedingMeasurements = Measurements.find({
        device_id: event.deviceId,
        // timestamp_ms: {$gte: eventTimestampRange.endTime.getTime(), $lte: proceedingTimestamp}
        timestamp_ms: {$gte: lastMeasurementTimestamp, $lte: proceedingTimestamp}
      }, {}).fetch();

      return {eventMeasurements, precedingMeasurements, proceedingMeasurements};
    }

  }
});