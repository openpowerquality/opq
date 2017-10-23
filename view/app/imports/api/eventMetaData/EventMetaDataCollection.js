import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';
import { check, Match } from 'meteor/check';

/**
 * EventMetaData collection.
 */
class EventMetaDataCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('EventMetaData',
        'events', // Must match remote collection name, which is 'events'.
        new SimpleSchema({
          type: {type: String},
          event_number: {type: Number},
          description: {type: String},
          boxes_triggered: {type: [Number]},
          boxes_received: {type: [Number]},
          event_start: {type: Number},
          event_end: {type: Number},
          time_stamp: {type: [Number]} // For research data; OpqView can ignore this.
        }),
        Meteor.settings.opqRemoteMongoUrl
    );

    this.publicationNames = {
      GET_EVENT_META_DATA: 'get_event_meta_data'
    };
  }

  /**
   * Loads all publications related to this collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() {
    if (Meteor.isServer) {
      const eventMetaDataCollectionPublications = require('./EventMetaDataCollectionPublications.js').eventMetaDataCollectionPublications;
      eventMetaDataCollectionPublications();
    }
  }

  queryConstructors() {
    return {
      getEventMetaData({startTime, endTime}) {
        check(startTime, Match.Maybe(Number));
        check(endTime, Match.Maybe(Number));

        const selector = {};
        if (startTime) selector.event_start = {$gte: startTime};
        if (endTime) selector.event_end = {$lte: endTime};

        return selector;
      }
    }
  }

}

/**
 * Provides the singleton instance of this class.
 * @type {EventMetaDataCollection}
 */
export const EventMetaData = new EventMetaDataCollection();
