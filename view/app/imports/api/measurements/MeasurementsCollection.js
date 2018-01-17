import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { progressBarSetup } from '../../modules/utils';

class MeasurementsCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    super('measurements', new SimpleSchema({
      box_id: { type: String },
      timestamp_ms: { type: Number },
      voltage: { type: Number },
      frequency: { type: Number },
    }));

    this.publicationNames = {
      RECENT_MEASUREMENTS: 'recent_measurements',
    };
  }

  /**
   * Defines a new Measurement document.
   * @param {String} box_id - The OPQBox's id value (not Mongo ID)
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the measurement.
   * @param {Number} voltage - The voltage measurement.
   * @param {Number} frequency - The frequency measurement.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency }) {
    const docID = this._collection.insert({ box_id, timestamp_ms, voltage, frequency });
    return docID;
  }

  /**
   * Returns an object representing a single Measurement.
   * @param {Object} docID - The Mongo.ObjectID of the Measurement.
   * @returns {Object} - An object representing a single Measurement.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const box_id = doc.box_id;
    const timestamp_ms = doc.timestamp_ms;
    const voltage = doc.voltage;
    const frequency = doc.frequency;

    return { box_id, timestamp_ms, voltage, frequency };
    /* eslint-enable camelcase */
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('measurementsIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    // Get all OpqBox IDs.
    const boxIDs = OpqBoxes.find().map(doc => doc.box_id);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid) {
        // eslint-disable-next-line max-len
        problems.push(`Measurements document failed schema validation: ${doc._id} (Invalid keys: ${validationContext.invalidKeys()})`);
      }
      validationContext.resetValidation();

      // Ensure box_id of the measurement exists in opq_boxes collection.
      if (!boxIDs.includes(doc.box_id)) {
        problems.push(`Measurement box_id does not exist in opq_boxes collection: ${doc}`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to the Measurements collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() { // eslint-disable-line class-methods-use-this
    if (Meteor.isServer) {
      Meteor.publish(this.publicationNames.RECENT_MEASUREMENTS, function (startTimeSecondsAgo, deviceId) {
        check(startTimeSecondsAgo, Number);
        check(deviceId, Number);

        const self = this;

        // const userId = this.userId;
        // if (!userId) throw new Meteor.Error('publications.notLoggedIn', 'Must log in to access page.');

        const startTimeMs = Date.now() - (startTimeSecondsAgo * 1000);
        // eslint-disable-next-line max-len
        const publishedMeasurementsMap = new Map(); // {timestamp: id} - To keep track of currently published measurements.

        const selector = (deviceId) ? {
          device_id: deviceId,
          timestamp_ms: { $gte: startTimeMs },
        } : { timestamp_ms: { $gte: startTimeMs } };

        let init = true;
        const measurementsHandle = this.find(selector, {
          fields: { _id: 1, timestamp_ms: 1, voltage: 1, frequency: 1, device_id: 1 },
          pollingIntervalMs: 1000,
        }).observeChanges({
          added: function (id, fields) {
            publishedMeasurementsMap.set(fields.timestamp_ms, id);
            self.added('measurements', id, fields);

            if (!init) {
              const startTime = Date.now() - (startTimeSecondsAgo * 1000);
              // Note: (_id, timestamp) corresponds to (value, key); for some reason Map's foreach is called this way.
              publishedMeasurementsMap.forEach((_id, timestamp) => {
                if (timestamp < startTime) {
                  self.removed('measurements', _id);
                  publishedMeasurementsMap.delete(timestamp);
                }
              });
            }
          },
        });
        init = false;
        self.ready();
        self.onStop(function () {
          measurementsHandle.stop();
        });
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {MeasurementsCollection}
 */
export const Measurements = new MeasurementsCollection();
