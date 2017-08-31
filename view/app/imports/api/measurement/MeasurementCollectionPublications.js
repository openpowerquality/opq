import { Meteor } from 'meteor/meteor';
import { Measurements } from './MeasurementCollection.js';

export const measurementCollectionPublications = () => {
  Meteor.publish(Measurements.publicationNames.RECENT_MEASUREMENTS, function (startTimeSecondsAgo, deviceId) {
    check(startTimeSecondsAgo, Number);
    const self = this;


    // const userId = this.userId;
    // if (!userId) throw new Meteor.Error('publications.notLoggedIn', 'Must log in to access page.');

    const startTimeMs = Date.now() - (startTimeSecondsAgo * 1000);
    const publishedMeasurementsMap = new Map(); // {timestamp: id} - To keep track of currently published measurements.

    const selector = (deviceId) ? {
      device_id: deviceId,
      timestamp_ms: {$gte: startTimeMs}
    } : {timestamp_ms: {$gte: startTimeMs}};

    let init = true;
    const measurementsHandle = Measurements.find(selector, {
      fields: {_id: 1, timestamp_ms: 1, voltage: 1, frequency: 1, device_id: 1},
      pollingIntervalMs: 1000
    }).observeChanges({
      added: function (id, fields) {
        publishedMeasurementsMap.set(fields.timestamp_ms, id);
        self.added('measurements', id, fields);

        if (!init) {
          const startTime = Date.now() - (startTimeSecondsAgo * 1000);
          publishedMeasurementsMap.forEach((id, timestamp) => { // Note: (id, timestamp) corresponds to (value, key)
            if (timestamp < startTime) {
              self.removed('measurements', id);
              publishedMeasurementsMap.delete(timestamp);
            }
          });
        }
      }
    });
    init = false;
    self.ready();
    self.onStop(function () {
      measurementsHandle.stop();
    });
  });
};