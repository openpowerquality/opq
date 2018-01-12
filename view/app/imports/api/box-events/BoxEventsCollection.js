import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection';
import { progressBarSetup } from "../../modules/utils";

/**
 * Collection class for the box_events collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#box_events
 */
class BoxEventsCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('box_events',
        new SimpleSchema({
          event_id: {type: Number},
          box_id: {type: String},
          event_start_timestamp_ms: {type: Number},
          event_end_timestamp_ms: {type: Number},
          window_timestamps_ms: {type: [Number]}, // For research purposes.
          thd: {type: Number},
          itic: {type: String},
          location: {type: Object, optional: true},
          'location.start_time': {type: Number},
          'location.zipcode': {type: Number},
          data_fs_filename: {type: String} // Stores the GridFs filename. Format is 'event_eventNumber_boxId'
        })
    );

    this.publicationNames = {
      EVENT_DATA: 'event_data'
    };
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
    const docID = this._collection.insert({ event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename });
    return docID;
  }

  /**
   * Returns an object representing a single BoxEvent.
   * @param {Object} docID - The Mongo.ObjectID of the BoxEvent.
   * @returns {Object} - An object representing a single BoxEvent.
   */
  dumpOne(docID) {
    const doc = this.findDoc(docID);
    const event_id = doc.event_id;
    const box_id = doc.box_id;
    const event_start = doc.event_start;
    const event_end = doc.event_end;
    const window_timestamps = doc.window_timestamps;
    const thd = doc.thd;
    const itic = doc.itic;
    const location = doc.location;
    const data_fs_filename = doc.data_fs_filename;

    return { event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename }
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
      if (!validationContext.isValid) {
        problems.push(`BoxEvent document failed schema validation: ${doc._id} (Invalid keys: ${validationContext.invalidKeys()})`);
      }
      validationContext.resetValidation();

      // Ensure event_id points to an existing Event document.
      if (Events.find({event_id: doc.event_id}).count() < 1) {
        problems.push(`BoxEvent event_id does not exist in Events collection: ${doc._id}`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to this collection.
   */
  publish() {
    if (Meteor.isServer) {

    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {BoxEventsCollection}
 */
export const BoxEvents = new BoxEventsCollection();