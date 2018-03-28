import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection.js';
import { BoxEvents } from '../box-events/BoxEventsCollection.js';
import { Measurements } from '../measurements/MeasurementsCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection.js';
import { Trends } from '../trends/TrendsCollection.js';
import { UserProfiles } from '../users/UserProfilesCollection.js';

/* eslint-disable indent */

class SystemStatsCollection extends BaseCollection {

  /**
   * Creates the System Stats collection.
   */
  constructor() {
    super('system_stats', new SimpleSchema({
      events_count: Number,
      box_events_count: Number,
      measurements_count: Number,
      opq_boxes_count: Number,
      trends_count: Number,
      users_count: Number,
      timestamp: Date,
      box_trend_stats: { type: Array },
      'box_trend_stats.$': { type: Object, blackbox: true },
    }));
  }

  /**
   * Defines a new SystemStats document.
   * @param {Number} events_count - The total number of Events documents.
   * @param {Number} box_events_count - The total number of BoxEvents documents.
   * @param {Number} measurements_count - The total number of Measurements documents.
   * @param {Number} opq_boxes_count - The total number of OpqBoxes documents.
   * @param {Number} trends_count - The total number of Trends documents.
   * @param {Number} users_count - The total number of Users.
   * @param {Object} box_trend_stats - Summary stats on trends for each box.
   * @returns The newly created document ID.
   */
  define({ events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count,
           box_trend_stats }) {
    const docID = this._collection.insert({ events_count, box_events_count, measurements_count, opq_boxes_count,
      trends_count, users_count, timestamp: new Date(), box_trend_stats });
    return docID;
  }

  /**
   * Returns an object representing a single SystemStats.
   * @param {Object} docID - The Mongo.ObjectID of the SystemStat.
   * @returns {Object} - An object representing a single SystemStat.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const events_count = doc.events_count;
    const box_events_count = doc.box_events_count;
    const measurements_count = doc.measurements_count;
    const opq_boxes_count = doc.opq_boxes_count;
    const trends_count = doc.trends_count;
    const users_count = doc.users_count;
    const timestamp = doc.timestamp;
    const box_trend_stats = doc.box_trend_stats;
    return { events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count,
      timestamp, box_trend_stats };
    /* eslint-enable camelcase */
  }

  /**
   * No need to check integrity for this collection.
   * @returns {Array}
   */
  checkIntegrity() { // eslint-disable-line
    const problems = [];
    return problems;
  }

  /**
   * Return an object with the following fields:
   * boxId: The ID of the box associated with this trend data.
   * firstTrend: A number (UTC timestamp) of the earliest trend data for this box, or 0 if not found.
   * latestTrend: A number (UTC timestamp) of the latest trend data for this box, or 0 if not found.
   * totalTrends: A Number indicating the total number of trends.
   * @param boxId The box ID.
   * @returns An object { boxId, firstTrend, lastTrend, totalTrends }.
   */
  getBoxTrendStat(boxId) { // eslint-disable-line
    const firstTrendDoc = Trends.oldestTrend(boxId);
    const firstTrend = firstTrendDoc ? firstTrendDoc.timestamp_ms : 0;
    const lastTrendDoc = Trends.newestTrend(boxId);
    const lastTrend = lastTrendDoc ? lastTrendDoc.timestamp_ms : 0;
    const totalTrends = Trends.countTrends(boxId);
    return { boxId, firstTrend, lastTrend, totalTrends };
  }

  updateCounts() {
    // Get current collection counts
    const events_count = Events.count();
    const box_events_count = BoxEvents.count();
    const measurements_count = Measurements.count();
    const opq_boxes_count = OpqBoxes.count();
    const trends_count = Trends.count();
    const users_count = UserProfiles.count(); // Not a base-collection class.
    const box_trend_stats = OpqBoxes.findBoxIds().map(boxId => this.getBoxTrendStat(boxId));

    // Ensure there is only one document in the collection. We will only update this one document with current stats.
    const count = this._collection.find().count();
    if (count > 1) {
      // Remove all documents but one, which we choose arbitrarily
      const doc = this._collection.findOne();
      this._collection.remove({ _id: { $ne: doc._id } });
    } else if (count < 1) {
      // Create new doc. Should only theoretically have to be done once, when we first create the collection.
      // eslint-disable-next-line max-len
      return this.define({ events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count, box_trend_stats });
    }

    // Update the one document with current collection counts.
    const systemStatsDoc = this._collection.findOne();
    return systemStatsDoc && this._collection.update(systemStatsDoc._id, {
      $set: { events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count,
        timestamp: new Date(), box_trend_stats },
    });
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {SystemStatsCollection}
 */
export const SystemStats = new SystemStatsCollection();