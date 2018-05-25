import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import { check } from 'meteor/check';
import BaseCollection from '../base/BaseCollection.js';
// import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/**
 * The trends collection provides long term OPQBox trend data.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#trends}
 */
class TrendsCollection extends BaseCollection {

  constructor() {
    super('trends', new SimpleSchema({
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
      TRENDS_AFTER_TIMESTAMP: 'trends_after_timestamp',
    };
    if (Meteor.server) {
      this._collection.rawCollection().createIndex({ timestamp_ms: 1, box_id: 1 }, { background: true });
    }
  }

  /**
   * Defines a new Trends document.
   * @param {String} box_id - The OPQBox's id. Must be defined.
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the trend.
   * @param {Number} voltage - The voltage trend object.
   * @param {Number} frequency - The frequency trend object.
   * @param {Number} thd - The thd trend object.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency, thd }) {
    // TODO: Need to check that box_id is valid.
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

      Meteor.publish(this.publicationNames.TRENDS_AFTER_TIMESTAMP, ({ timestamp, boxIDs }) => {
        check(timestamp, Number);
        check(boxIDs, [String]);
        return this.find({ timestamp_ms: { $gte: timestamp }, box_id: { $in: boxIDs } });
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {TrendsCollection}
 */
export const Trends = new TrendsCollection();
