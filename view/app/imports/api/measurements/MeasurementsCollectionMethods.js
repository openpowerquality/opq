import { Mongo } from 'meteor/mongo';
import _ from 'lodash';
import Moment from 'moment';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { Measurements } from './MeasurementsCollection.js';
import { Events } from '../events/EventsCollection.js';

export const totalMeasurementsCount = new ValidatedMethod({
  name: 'Measurements.totalMeasurementsCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return Measurements.find({}).count();
  },
});

export const checkBoxStatus = new ValidatedMethod({
  name: 'Measurements.checkBoxStatus',
  validate: new SimpleSchema({
    box_id: { type: String },
  }).validator({ clean: true }),
  run({ box_id }) {
    if (!this.isSimulation) {
      const oneMinuteAgo = Moment().subtract(60, 'seconds').valueOf();
      const measurements = Measurements.findOne({ box_id, timestamp_ms: { $gte: oneMinuteAgo } });
      return !!measurements;
    }
    return null;
  },
});

export const activeBoxIDs = new ValidatedMethod({
  name: 'Measurements.activeBoxIDs',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    if (!this.isSimulation) {
      const oneMinuteAgo = Moment().subtract(60, 'seconds').valueOf();
      const measurements = Measurements.find({ timestamp_ms: { $gte: oneMinuteAgo } }).fetch();
      if (measurements.length > 0) {
        return _.uniq(_.map(measurements, 'box_id'));
      }
    }
    return null;
  },
});

export const getActiveBoxIds = new ValidatedMethod({
  name: 'Measurements.getActiveBoxIds',
  validate: new SimpleSchema({
    startTimeMs: { type: Number },
  }).validator({ clean: true }),
  run({ startTimeMs }) {
    const recentMeasurements = Measurements.find({
      timestamp_ms: { $gte: startTimeMs },
    }, {
      fields: { box_id: 1 },
    }).fetch();

    // Returns an array of unique deviceIds, sorted asc.
    return (recentMeasurements.length > 0)
      ? _.uniq(_.pluck(recentMeasurements, 'box_id')).sort((a, b) => a - b)
      : null;
  },
});

export const getEventMeasurementsByMetaDataId = new ValidatedMethod({
  name: 'Measurements.getEventMeasurementsByMetaDataId',
  validate: new SimpleSchema({
    eventMetaDataId: { type: Mongo.ObjectID },
  }).validator({ clean: true }),
  run({ eventMetaDataId }) {
    if (!this.isSimulation) {
      const eventMetaData = Events.findOne({ _id: eventMetaDataId });

      const eventMeasurements = Measurements.find({
        box_id: eventMetaData.boxes_triggered[0], // Just look at first triggering device for now.
        timestamp_ms: { $gte: eventMetaData.event_start, $lte: eventMetaData.event_end },
      }, {
        sort: { event_end: 1 },
      }).fetch();

      const firstMeasurementTimestamp = eventMeasurements[0].timestamp_ms;
      const lastMeasurementTimestamp = eventMeasurements[eventMeasurements.length - 1].timestamp_ms;

      // Let's also retrieve some measurements preceding and proceeding event range. 20% of event range on both sides.
      const eventDurationMs = (eventMetaData.event_end - eventMetaData.event_start);
      const precedingTimestamp = eventMetaData.event_start - (eventDurationMs * 0.2);
      const proceedingTimestamp = eventMetaData.event_end + (eventDurationMs * 0.2);

      const precedingMeasurements = Measurements.find({
        box_id: eventMetaData.boxes_triggered[0],
        timestamp_ms: { $gte: precedingTimestamp, $lte: firstMeasurementTimestamp },
      }, {}).fetch();

      const proceedingMeasurements = Measurements.find({
        box_id: eventMetaData.boxes_triggered[0],
        timestamp_ms: { $gte: lastMeasurementTimestamp, $lte: proceedingTimestamp },
      }, {}).fetch();

      return { eventMeasurements, precedingMeasurements, proceedingMeasurements };
    }

    return null;
  },
});

export const getEventMeasurements = new ValidatedMethod({
  name: 'Measurements.getEventMeasurements',
  validate: new SimpleSchema({
    box_id: { type: Number, optional: true }, // Get rid of optional later.
    startTime: { type: Number, optional: true },
    endTime: { type: Number, optional: true },
  }).validator({ clean: true }),
  run({ box_id, startTime, endTime }) {
    if (!this.isSimulation) {
      console.log(box_id, startTime, endTime);
      const eventMeasurements = Measurements.find({
        box_id,
        timestamp_ms: { $gte: startTime, $lte: endTime },
      }, {
        sort: { timestamp_ms: 1 },
      }).fetch();

      const firstMeasurementTimestamp = eventMeasurements[0].timestamp_ms;
      const lastMeasurementTimestamp = eventMeasurements[eventMeasurements.length - 1].timestamp_ms;

      // Let's also retrieve some measurements preceding and proceeding event range. 20% of event range on both sides.
      const duration = (endTime - startTime);
      const precedingTimestamp = startTime - (duration * 15.0);
      const proceedingTimestamp = endTime + (duration * 15.0);

      const precedingMeasurements = Measurements.find({
        box_id,
        timestamp_ms: { $gte: precedingTimestamp, $lte: firstMeasurementTimestamp },
      }, {}).fetch();

      const proceedingMeasurements = Measurements.find({
        box_id,
        timestamp_ms: { $gte: lastMeasurementTimestamp, $lte: proceedingTimestamp },
      }, {}).fetch();

      return { eventMeasurements, precedingMeasurements, proceedingMeasurements };
    }
    return null;
  },
});

export const dygraphMergeDatasets = (xFieldName, yFieldName, ...datasets) => {
  const mergedData = new Map();
  const numDatasets = datasets.length;

  datasets.forEach((dataset, index) => {
    // Dygraph requires a data format of:
    // [
    //  [x1, y1, y2, y3, ...],
    //  [x2, y1, y2, y3, ...]
    // ]
    // Where x is the independent variable and y is the dependant variable. As such, the y1 column represents a dataset,
    // the y2 column represents another dataset, and the y3 column represents the final dataset. Dygraph will expect
    // null when there is no value for a given dataset.
    //
    // As such, when iterating through our datasets, we need to insert data at appropriate index of array, and so we
    // must keep track of correct index to write into.
    const writeIndex = index;
    dataset.forEach(data => {
      const x = data[xFieldName];
      const y = data[yFieldName];

      if (mergedData.has(x)) {
        // Get the array and update at appropriate index.
        const arr = mergedData.get(x);
        arr[writeIndex] = y;
        mergedData.set(x, arr);
      } else {
        // Create a null filled array of length equal to number of datasets.
        const newArr = new Array(numDatasets).fill(null);
        newArr[writeIndex] = y; // Set the y value at the proper index.
        mergedData.set(x, newArr);
      }
    });
  });

  const mergedDataset = Array.from(mergedData.keys()).map(key => [key, ...mergedData.get(key)]);

  // Sort by the independent variable, which is the 0th index of each array.
  mergedDataset.sort((a, b) => a[0] - b[0]);

  return mergedDataset;
};


export const getLatestMeasurement = new ValidatedMethod({
  name: 'Measurements.getLatestMeasurement',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return Measurements.findOne({}, { sort: { timestamp_ms: -1 } });
  },
});
