import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import moment from 'moment';
import { check } from 'meteor/check';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

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
    OpqBoxes.assertValidBoxId(box_id);
    timestamp_ms = moment(timestamp_ms).valueOf(); // eslint-disable-line
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
   * Called by the dailyTrends Meteor Method to return an object containing Trend data (min, max, average) rolled up
   * to the day level for the specified set of boxes.
   * @param boxIDs An array of boxIDs.
   * @param startDate_ms The start date in milliseconds.
   * @param endDate_ms The end data in milliseconds.
   */
  dailyTrends({ boxIDs, startDate_ms, endDate_ms }) {
    const trendDict = {};
    const self = this;
    boxIDs.forEach(function (box_id) { trendDict[box_id] = self.dailyTrendsBox(startDate_ms, endDate_ms, box_id); });
    return trendDict;
  }

  /**
   * Returns an object whose keys are dates (utc milliseconds) and values are dailyTrendData objects.
   * @param startDate The first day to provide trend data for.
   * @param endDate The last day to provide trend data for.
   * @param box_id The box_id.
   * @returns An object with daily trend data for the date interval.
   */
  dailyTrendsBox(startDate, endDate, box_id) {
    const dailyTrends = {};
    for (let day = moment(startDate).startOf('day'); day <= moment(endDate).startOf('day'); day = day.add(1, 'days')) {
      dailyTrends[day.valueOf()] = this.dailyTrendBoxDay(day, box_id);
    }
    return dailyTrends;
  }

  /**
   * Returns an object with min, max, and average values of voltage, frequency, and THD for the given day and box_id.
   * @param day A Date object indicating the day of interest. Must be valid argument to Moment.
   * @param box_id A string with a box_id.
   * @returns An object with top-level fields frequency, voltage, and thd. The value of each of those fields is another
   * object with fields min, max, and average. If there is no
   * data for the top-level field for the given day, then zero is returned for min, max, and average.
   * @throws { Meteor.Error } If day is not a date or box_id is not a box_id.
   */
  dailyTrendBoxDay(day, box_id) {
    // Make sure day and box_id are valid.
    OpqBoxes.assertValidBoxId(box_id);
    const date = moment(day);
    if (!date.isValid()) {
      throw new Meteor.Error(`Invalid date passed to dailyTrendData: ${day}`);
    }
    // Get all the trend documents for this box and day.
    const startOfDay = moment(date).startOf('day').valueOf();
    const endOfDay = moment(date).endOf('day').valueOf();
    const docs = this.find({ box_id, timestamp_ms: { $gt: startOfDay, $lte: endOfDay } }).fetch();
    // Return an object with min, max, and average values of frequency, voltage, and thd, if present.
    // Or an empty object is there is no data for that day.
    const dataObject = {
      frequency: this._dailyTrendStats(docs, 'frequency'),
      voltage: this._dailyTrendStats(docs, 'voltage'),
      thd: this._dailyTrendStats(docs, 'thd'),
    };
    return (dataObject.frequency.count > 0) ? dataObject : {};
  }

  /**
   * Compute the min, max, average, and count of values for the passed field in the array of docs.
   * @param docs An array of documents (i.e. objects) which may or may not contain the passed field.
   * @param field The field of interest in the passed array of documents.
   * @returns An object with fields min, max, average, count.
   * If there are no values associated with the field of interest, then an object with the value 0 for
   * min, max, average, and count is returned.
   * @private
   */
  _dailyTrendStats(docs, field) {
    const fieldDocs = _.compact(_.pluck(docs, field));
    const minValues = _.pluck(fieldDocs, 'min');
    const maxValues = _.pluck(fieldDocs, 'max');
    const aveValues = _.pluck(fieldDocs, 'average');
    const averagefn = (vals) => ((vals.reduce((a, b) => (a + b), 0)) / vals.length);
    return (minValues.length > 0 && maxValues.length > 0 && aveValues.length > 0) ?
      { min: _.min(minValues), max: _.max(maxValues), average: averagefn(aveValues), count: minValues.length } :
      { min: 0, max: 0, average: 0, count: 0 };
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
