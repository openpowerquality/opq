import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

/**
 * Collection class for the box_events collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#box_events
 */
class EventDataCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    // Note: Event waveform data is stored in a variable named key in the format of 'events_requestId_deviceId'. As such
    // we cannot enforce these keys with SimpleSchema. Also note that each EventData document can contain multiple
    // device waveform data.
    super('BoxEvents',
        'box_events', // Has to match the remote collection name, which is 'data' at the moment.
        new SimpleSchema({
          event_id: {type: Number},
          box_id: {type: String},
          event_start: {type: Number},
          event_end: {type: Number},
          window_timestamps: {type: [Number]}, // For research purposes.
          thd: {type: Number},
          itic: {type: String},
          location: {type: Object},
          'location.start_time': {type: Number},
          'location.zipcode': {type: Number},
          data_fs_filename: {type: String} // Stores the GridFs filename. Format is 'event_eventNumber_boxId'
        }),
        Meteor.settings.opqRemoteMongoUrl
    );

    this.publicationNames = {
      EVENT_DATA: 'event_data',
      RECENT_EVENT_DATA: 'recent_event_data'
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

  /**
   * Loads all publications related to this collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() {
    if (Meteor.isServer) {
      const eventDataPublications = require('./EventDataCollectionPublications.js').eventDataCollectionPublications;
      eventDataPublications();
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {EventDataCollection}
 */
export const EventData = new EventDataCollection();