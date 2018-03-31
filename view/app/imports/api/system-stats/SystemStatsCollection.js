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
      events_count_today: Number,
      box_events_count: Number,
      box_events_count_today: Number,
      measurements_count: Number,
      measurements_count_today: Number,
      trends_count: Number,
      trends_count_today: Number,
      opq_boxes_count: Number,
      users_count: Number,
      timestamp: Date,
      box_trend_stats: { type: Array },
      'box_trend_stats.$': { type: Object, blackbox: true },
      health: { type: Array },
      'health.$': { type: Object, blackbox: true },
    }));
  }

  /**
   * Defines a new SystemStats document.
   * @param {Number} events_count - The total number of Events documents.
   * @param {Number} events_count_today - The total number of Events documents today.
   * @param {Number} box_events_count - The total number of BoxEvents documents.
   * @param {Number} box_events_count_today - The total number of BoxEvents documents today.
   * @param {Number} measurements_count - The total number of Measurements documents.
   * @param {Number} measurements_count_today - The total number of Measurements documents today.
   * @param {Number} opq_boxes_count - The total number of OpqBoxes documents.
   * @param {Number} trends_count - The total number of Trends documents.
   * @param {Number} trends_count_today - The total number of Trends documents today.
   * @param {Number} users_count - The total number of Users.
   * @param {Object} box_trend_stats - Summary stats on trends for each box.
   * @param {Object} health - Health status of all boxes and services.
   * @returns The newly created document ID.
   */
  define({ events_count, events_count_today, box_events_count, box_events_count_today, measurements_count,
           measurements_count_today, opq_boxes_count, trends_count, trends_count_today, users_count,
           box_trend_stats, health }) {
    const docID = this._collection.insert({ events_count, box_events_count, measurements_count, opq_boxes_count,
      trends_count, users_count, timestamp: new Date(), box_trend_stats, health,
    events_count_today, box_events_count_today, measurements_count_today, trends_count_today });
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
    const events_count_today = doc.events_count_today;
    const box_events_count = doc.box_events_count;
    const box_events_count_today = doc.box_events_count_today;
    const measurements_count = doc.measurements_count;
    const measurements_count_today = doc.measurements_count_today;
    const trends_count = doc.trends_count;
    const trends_count_today = doc.trends_count_today;
    const opq_boxes_count = doc.opq_boxes_count;
    const users_count = doc.users_count;
    const timestamp = doc.timestamp;
    const box_trend_stats = doc.box_trend_stats;
    return { events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count,
      timestamp, box_trend_stats, events_count_today, box_events_count_today, measurements_count_today,
    trends_count_today};
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

  /**
   * Create an array of objects with fields: name, icon, color
   * We just display convert this array to labels to display health.
   */
  getHealthArray() {
    const health = [];
    health.push({ name: 'Mauka', icon: 'check circle', color: 'green' });
    health.push({ name: 'Makai', icon: 'warning circle', color: 'red' });
    OpqBoxes.findBoxIds().forEach(function (boxId) {
      health.push({ name: `Box ${boxId}`, icon: 'help circle', color: 'grey' });
    });
    return health;
  }

  updateCounts() {
    // Get current collection counts
    const events_count = Events.count();
    const events_count_today = Events.countToday('target_event_start_timestamp_ms');
    const box_events_count = BoxEvents.count();
    const box_events_count_today = BoxEvents.countToday('event_start_timestamp_ms');
    const measurements_count = Measurements.count();
    const measurements_count_today = Measurements.countToday('timestamp_ms');
    const opq_boxes_count = OpqBoxes.count();
    const trends_count = Trends.count();
    const trends_count_today = Trends.countToday('timestamp_ms');
    const users_count = UserProfiles.count(); // Not a base-collection class.
    const box_trend_stats = OpqBoxes.findBoxIds().map(boxId => this.getBoxTrendStat(boxId));
    const health = this.getHealthArray();

    // Ensure there is only one document in the collection. We will only update this one document with current stats.
    const count = this._collection.find().count();
    if (count > 1) {
      // Remove all documents but one, which we choose arbitrarily
      const doc = this._collection.findOne();
      this._collection.remove({ _id: { $ne: doc._id } });
    } else if (count < 1) {
      // Create new doc. Should only theoretically have to be done once, when we first create the collection.
      // eslint-disable-next-line max-len
      return this.define({ events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count, box_trend_stats, health, events_count_today, box_events_count_today, measurements_count_today,
      trends_count_today });
    }

    // Update the one document with current collection counts.
    const systemStatsDoc = this._collection.findOne();
    return systemStatsDoc && this._collection.update(systemStatsDoc._id, {
      $set: { events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count,
        timestamp: new Date(), box_trend_stats, health, events_count_today, box_events_count_today,
        measurements_count_today, trends_count_today },
    });
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {SystemStatsCollection}
 */
export const SystemStats = new SystemStatsCollection();
