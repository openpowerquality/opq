import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

class EventDataCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    // Note: Event waveform data is stored in a variable named key in the format of 'events_requestId_deviceId'. As such
    // we cannot enforce these keys with SimpleSchema. Also note that each EventData document can contain multiple
    // device waveform data.
    super('EventData',
        'data', // Has to match the remote collection name, which is 'data' at the moment.
        new SimpleSchema({
          box_id: {type: Number},
          event_start: {type: Number},
          event_end: {type: Number},
          event_number: {type: Number},
          time_stamp: {type: [Number]}, // For research purposes; OPQView can ignore.
          //data: {type: [Number]} // These values need to be divided by device calibration constant.
          data: {type: String} // Stores the GridFs filename. Format is 'event_eventNumber_boxId'
        }),
        Meteor.settings.opqRemoteMongoUrl
    );

    this.publicationNames = {
      EVENT_DATA: 'event_data',
      RECENT_EVENT_DATA: 'recent_event_data'
    };
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