import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';
import { check, Match } from 'meteor/check';

class BoxEventCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    super('BoxEvent',
        'boxEvents',
        new SimpleSchema({
          deviceId: {type: Number},
          eventType: {type: String},
          eventStart: {type: Date},
          eventEnd: {type: Date},
          percent: {type: Number},
          reqId: {type: Number}
        }),
        Meteor.settings.opqRemoteMongoUrl
    );

    this.publicationNames = {
      RECENT_BOX_EVENTS: 'recent_box_events',
      COMPLETE_RECENT_BOX_EVENTS: 'complete_recent_box_events',
      DAILY_BOX_EVENTS: 'daily_box_events',
      GET_BOX_EVENTS: 'get_box_events'
    };
  }

  /**
   * Loads all publications related to this collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() {
    if (Meteor.isServer) {
      const boxEventPublications = require('./BoxEventCollectionPublications.js').boxEventCollectionPublications;
      boxEventPublications();
    }
  }

  queryConstructors() {
    return {
      getBoxEvents({startTime, endTime}) {
        check(startTime, Date);
        check(endTime, Match.Maybe(Date)); // Optional

        // Null or undefined endTime indicates we want all events > startTime
        const selector = (!endTime) ? {eventStart: {$gte: new Date(startTime)}}
                                    : {eventStart: {$gte: new Date(startTime)}, eventEnd: {$lte: new Date(endTime)}};

        return selector;
      }
    }
  }

}

/**
 * Provides the singleton instance of this class.
 * @type {BoxEventCollection}
 */
export const BoxEvents = new BoxEventCollection();

Meteor.startup(() => {
  if (Meteor.isServer) {
    // BoxEvents._collection._ensureIndex({eventStart: -1, eventEnd: -1});
    // BoxEvents._collection._ensureIndex({eventStart: -1});
    // BoxEvents._collection._ensureIndex({eventEnd: -1});
  }

});
