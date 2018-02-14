import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection.js';
import { BoxEvents } from '../box-events/BoxEventsCollection.js';
import { Measurements } from '../measurements/MeasurementsCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection.js';
import { Trends } from '../trends/TrendsCollection.js';
import { Users } from '../users/UsersCollection.js';
import { progressBarSetup } from '../../modules/utils';

class SystemStatsCollection extends BaseCollection {

  /**
   * Creates the Trends collection.
   */
  constructor() {
    super('system_stats', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      events_count: { type: Number },
      box_events_count: { type: Number },
      measurements_count: { type: Number },
      opq_boxes_count: { type: Number },
      trends_count: { type: Number },
      users_count: { type: Number },
    }));

    this.publicationNames = {
      GET_SYSTEM_STATS: 'get_system_stats',
    };
  }

  /**
   * Defines a new SystemStats document.
   * @param {Number} events_count - The total number of Events documents.
   * @param {Number} box_events_count - The total number of BoxEvents documents.
   * @param {Number} measurements_count - The total number of Measurements documents.
   * @param {Number} opq_boxes_count - The total number of OpqBoxes documents.
   * @param {Number} trends_count - The total number of Trends documents.
   * @param {Number} users_count - The total number of Users.
   * @returns The newly created document ID.
   */
  define({ events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count }) {
    const docID = this._collection.insert({ events_count, box_events_count, measurements_count, opq_boxes_count,
      trends_count, users_count });
    return docID;
  }

  /**
   * Loads all publications related to the Trends collection.
   */
  publish() { // eslint-disable-line class-methods-use-this
    if (Meteor.isServer) {
      const self = this;

      Meteor.publish(this.publicationNames.GET_SYSTEM_STATS, function () {
        return self.find({});
      });
    }
  }

  updateCounts() {
    // Get current collection counts
    const events_count = Events.count();
    const box_events_count = BoxEvents.count();
    const measurements_count = Measurements.count();
    const opq_boxes_count = OpqBoxes.count();
    const trends_count = Trends.count();
    const users_count = Users.find({}).count(); // Not a base-collection class.

    // Ensure there is only one document in the collection. We will only update this one document with current stats.
    const count = this._collection.find().count();
    if (count > 1) {
      // Remove all documents but one, which we choose arbitrarily
      const doc = this._collection.findOne();
      this._collection.remove({ _id: { $ne: doc._id } });
    } else if (count < 1) {
      // Create new doc. Should only theoretically have to be done once, when we first create the collection.
      // eslint-disable-next-line max-len
      return this.define({ events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count });
    }

    // Update the one document with current collection counts.
    const systemStatsDoc = this._collection.findOne();
    return this._collection.update({ _id: systemStatsDoc._id }, {
      $set: { events_count, box_events_count, measurements_count, opq_boxes_count, trends_count, users_count },
    });
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {SystemStatsCollection}
 */
export const SystemStats = new SystemStatsCollection();
