import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Measurements } from './MeasurementCollection.js';
import { EventMetaData } from '../eventMetaData/EventMetaDataCollection.js';

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
    eventMetaDataId: {type: Mongo.ObjectID}
  }).validator({clean: true}),
  run({ eventMetaDataId }) {
    if (!this.isSimulation) {
      const eventMetaData = EventMetaData.findOne({_id: eventMetaDataId});

      const eventMeasurements = Measurements.find({
        device_id: eventMetaData.boxes_triggered[0], // Just look at first triggering device for now.
        timestamp_ms: {$gte: eventMetaData.event_start, $lte: eventMetaData.event_end}
      }, {
        sort: {event_end: 1}
      }).fetch();

      const firstMeasurementTimestamp = eventMeasurements[0].timestamp_ms;
      const lastMeasurementTimestamp = eventMeasurements[eventMeasurements.length - 1].timestamp_ms;

      // Let's also retrieve some measurements preceding and proceeding event range. 20% of event range on both sides.
      const eventDurationMs = (eventMetaData.event_end - eventMetaData.event_start);
      const precedingTimestamp = eventMetaData.event_start - (eventDurationMs * 0.2);
      const proceedingTimestamp = eventMetaData.event_end + (eventDurationMs * 0.2);

      const precedingMeasurements = Measurements.find({
        device_id: eventMetaData.boxes_triggered[0],
        timestamp_ms: {$gte: precedingTimestamp, $lte: firstMeasurementTimestamp}
      }, {}).fetch();

      const proceedingMeasurements = Measurements.find({
        device_id: eventMetaData.boxes_triggered[0],
        timestamp_ms: {$gte: lastMeasurementTimestamp, $lte: proceedingTimestamp}
      }, {}).fetch();

      return {eventMeasurements, precedingMeasurements, proceedingMeasurements};
    }

  }
});