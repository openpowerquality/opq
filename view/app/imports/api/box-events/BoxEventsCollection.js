import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection';
import { progressBarSetup } from '../../modules/utils';

/**
 * BoxEvents provides event meta-data for a given OPQ Box.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#box-events}
 */
class BoxEventsCollection extends BaseCollection {

  constructor() {
    super('box_events', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      event_id: Number,
      box_id: String,
      event_start_timestamp_ms: Number,
      event_end_timestamp_ms: Number,
      window_timestamps_ms: [Number], // For research purposes.
      thd: Number,
      itic: String,
      location: { type: Object, optional: true },
      'location.start_time': { type: Number, optional: true },
      'location.zipcode': { type: Number, optional: true },
      data_fs_filename: String, // Stores the GridFs filename. Format is 'event_eventNumber_boxId'
    }));

    this.publicationNames = {
      EVENT_DATA: 'event_data',
    };
    if (Meteor.server) {
      this._collection.rawCollection().createIndex({ event_start_timestamp_ms: 1, box_id: 1 }, { background: true });
    }
  }

  /**
   * Defines a new BoxEvent document.
   * @param {Number} event_id - The event_id associated with the BoxEvent.
   * @param {String} box_id - The box_id associated with the BoxEvent.
   * @param {Number} event_start - The start timestamp (unix milliseconds) of the event.
   * @param {Number} event_end - The end timestamp (unix milliseconds) of the event.
   * @param {[Number]} window_timestamps - An array of timestamps, for research purposes. See docs for details.
   * @param {Number} thd - The total harmonic distortion value of the event.
   * @param {String} itic - The ITIC value of the event.
   * @param {Object} location - The location of the OPQBox at the time of the event.
   * @param {String} data_fs_filename - The GridFS filename holding the actual event waveform data.
   * @returns The newly created document ID.
   */
  define({ event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename }) {
    const docID = this._collection.insert({
      event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename,
    });
    return docID;
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('boxEventsIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`BoxEvent document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();

      // Ensure event_id points to an existing Event document.
      if (Events.find({ event_id: doc.event_id }).count() < 1) {
        // eslint-disable-next-line max-len
        problems.push(`BoxEvent's event_id does not exist in Events collection: ${doc._id} (event_id: ${doc.event_id})`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /** Publications for this collection are disabled. */
  publish() { }
}

/**
 * Provides the singleton instance of this class.
 * @type {BoxEventsCollection}
 */
export const BoxEvents = new BoxEventsCollection();
