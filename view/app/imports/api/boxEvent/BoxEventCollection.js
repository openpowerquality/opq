import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

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
        'mongodb://localhost:3002/opq'
    );

    this.publicationNames = {
      RECENT_BOX_EVENTS: 'recent_box_events',
      COMPLETE_RECENT_BOX_EVENTS: 'complete_recent_box_events',
      DAILY_BOX_EVENTS: 'daily_box_events'
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
}

/**
 * Provides the singleton instance of this class.
 * @type {BoxEventCollection}
 */
export const BoxEvents = new BoxEventCollection();