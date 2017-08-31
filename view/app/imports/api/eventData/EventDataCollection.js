import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

class EventDataCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    // Note: Event waveform data is stored in a variable named key in the format of 'events_requestId_deviceId'. As such
    // we cannot enforce these keys with SimpleSchema. Also note that each EventData document can contain multiple
    // device waveform data.
    super('EventData',
        'data', // Has to match the remote collection name, which is 'data' at the moment.
        new SimpleSchema({
          request_id: {type: Number}
        }),
        'mongodb://localhost:3002/opq'
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