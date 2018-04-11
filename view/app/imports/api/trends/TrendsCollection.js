import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import { check } from 'meteor/check';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { progressBarSetup } from '../../modules/utils';

class TrendsCollection extends BaseCollection {

  /**
   * Creates the Trends collection.
   */
  constructor() {
    super('trends', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      box_id: { type: String },
      timestamp_ms: { type: Number },
      voltage: { type: Object },
      'voltage.min': { type: Number },
      'voltage.max': { type: Number },
      'voltage.average': { type: Number },
      frequency: { type: Object },
      'frequency.min': { type: Number },
      'frequency.max': { type: Number },
      'frequency.average': { type: Number },
      thd: { type: Object, optional: true },
      'thd.min': { type: Number },
      'thd.max': { type: Number },
      'thd.average': { type: Number },
    }));

    this.publicationNames = {
      GET_RECENT_TRENDS: 'get_recent_trends',
      TRENDS_RECENT_MONTH: 'trends_recent_month',
    };
    if (Meteor.server) {
      this._collection.rawCollection().createIndex({ timestamp_ms: 1, box_id: 1 }, { background: true });
    }
  }

  /**
   * Defines a new Trends document.
   * @param {String} box_id - The OPQBox's id value (not Mongo ID)
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the trend.
   * @param {Number} voltage - The voltage trend object.
   * @param {Number} frequency - The frequency trend object.
   * @param {Number} thd - The thd trend object.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency, thd }) {
    const docID = this._collection.insert({ box_id, timestamp_ms, voltage, frequency, thd });
    return docID;
  }

  /**
   * Returns the oldest Trend document associated with box_id by timestamp, or null if there are no Trends for box_id.
   * @param box_id The box_id
   * @returns The Trend document, or null.
   */
  oldestTrend(box_id) {
    return this._collection.findOne({ box_id, timestamp_ms: { $gt: 0 } }, { sort: { timestamp_ms: 1 } });
  }

  /**
   * Returns the newest Trend document associated with box_id by timestamp, or null if there are no Trends for box_id.
   * @param box_id The box_id
   * @returns The Trend document, or null.
   */
  newestTrend(box_id) {
    return this._collection.findOne({ box_id }, { sort: { timestamp_ms: -1 } });
  }

  /**
   * Returns the number of Trend documents associated with box_id.
   * @param box_id The box ID.
   * @returns The number of Trend documents with that ID.
   */
  countTrends(box_id) {
    return this._collection.find({ box_id }).count();
  }

  /**
   * Returns an object representing a single Trend.
   * @param {Object} docID - The Mongo.ObjectID of the Trend.
   * @returns {Object} - An object representing a single Trend.
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
    const validationContext = this.getSchema().namedContext('trendsIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    // Get all OpqBox IDs.
    const boxIDs = OpqBoxes.find().map(doc => doc.box_id);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`Trends document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();

      // Ensure box_id of the trend exists in opq_boxes collection.
      if (!boxIDs.includes(doc.box_id)) {
        problems.push(`Trends box_id does not exist in opq_boxes collection: ${doc.box_id} (docID: ${doc._id})`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to the Trends collection.
   */
  publish() { // eslint-disable-line class-methods-use-this
    if (Meteor.isServer) {
      const self = this;

      Meteor.publish(this.publicationNames.GET_RECENT_TRENDS, function ({ numTrends }) {
        check(numTrends, Number);

        const trends = self.find({}, { sort: { timestamp_ms: -1 }, limit: numTrends });
        return trends;
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {TrendsCollection}
 */
export const Trends = new TrendsCollection();
