import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { check } from 'meteor/check';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { progressBarSetup } from '../../modules/utils';

class MeasurementsCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    super('measurements', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      box_id: { type: String },
      timestamp_ms: { type: Number },
      voltage: { type: Number },
      frequency: { type: Number },
      thd: { type: Number, optional: true },
      expireAt: { type: Date },
    }));

    this.publicationNames = {
      RECENT_MEASUREMENTS: 'recent_measurements',
      BOX_MAP_MEASUREMENTS: 'box_map_measurements',
    };
    if (Meteor.server) {
      this._collection.rawCollection().createIndex({ timestamp_ms: 1, box_id: 1 }, { background: true });
    }
  }

  /**
   * Defines a new Measurement document.
   * @param {String} box_id - The OPQBox's id value (not Mongo ID)
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the measurement.
   * @param {Number} voltage - The voltage measurement.
   * @param {Number} frequency - The frequency measurement.
   * @param {Number} thd - The thd measurement.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency, thd }) {
    const docID = this._collection.insert({ box_id, timestamp_ms, voltage, frequency, thd });
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
    const thd = doc.thd;

    return { box_id, timestamp_ms, voltage, frequency, thd };
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
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`Measurements document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();

      // Ensure box_id of the measurement exists in opq_boxes collection.
      if (!boxIDs.includes(doc.box_id)) {
        problems.push(`Measurements box_id does not exist in opq_boxes collection: ${doc.box_id} (docID: ${doc._id})`);
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
      const self = this;

      Meteor.publish(this.publicationNames.BOX_MAP_MEASUREMENTS, function (boxIds) {
        check(boxIds, [String]);
        // Get measurements for each given box.
        // const now_ms = Date.now();
        const now_ms = self.findOne({}, { sort: { timestamp_ms: -1 } }).timestamp_ms;
        const measurements = self.find(
            { box_id: { $in: boxIds }, timestamp_ms: { $gte: now_ms } },
            {
              fields: { _id: 1, timestamp_ms: 1, voltage: 1, frequency: 1, thd: 1, box_id: 1 },
              sort: { timestamp_ms: -1 },
              limit: 20,
              pollingIntervalMs: 1000,
            },
        );
        return measurements;
      });

      Meteor.publish(this.publicationNames.RECENT_MEASUREMENTS, function (startTimeSecondsAgo, boxID) {
        check(startTimeSecondsAgo, Number);
        check(boxID, String);

        const instance = this;

        const startTimeMs = Date.now() - (startTimeSecondsAgo * 1000);
        // eslint-disable-next-line max-len
        const publishedMeasurementsMap = new Map(); // {timestamp: id} - To keep track of currently published measurements.

        const selector = (boxID) ? {
          box_id: boxID,
          timestamp_ms: { $gte: startTimeMs },
        } : { timestamp_ms: { $gte: startTimeMs } };

        let init = true;
        const measurementsHandle = self.find(selector, {
          fields: { _id: 1, timestamp_ms: 1, voltage: 1, frequency: 1, box_id: 1 },
          pollingIntervalMs: 1000,
        }).observeChanges({
          added: function (id, fields) {
            publishedMeasurementsMap.set(fields.timestamp_ms, id);
            instance.added('measurements', id, fields);

            if (!init) {
              const startTime = Date.now() - (startTimeSecondsAgo * 1000);
              // Note: (_id, timestamp) corresponds to (value, key); for some reason Map's foreach is called this way.
              publishedMeasurementsMap.forEach((_id, timestamp) => {
                if (timestamp < startTime) {
                  instance.removed('measurements', _id);
                  publishedMeasurementsMap.delete(timestamp);
                }
              });
            }
          },
        });
        init = false;
        instance.ready();
        instance.onStop(function () {
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
