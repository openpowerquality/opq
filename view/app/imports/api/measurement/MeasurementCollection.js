import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

class MeasurementCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    super('Measurement',
        'measurements',
        new SimpleSchema({
          device_id: {type: String},
          timestamp_ms: {type: Number},
          voltage: {type: Number},
          frequency: {type: Number}
        }),
        'mongodb://localhost:3002/opq'
    );

    this.publicationNames = {
      RECENT_MEASUREMENTS: 'recent_measurements'
    };
  }

  /**
   * Loads all publications related to the Measurements collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() {
    if (Meteor.isServer) {
      const measurementsPublications = require('./MeasurementCollectionPublications.js').measurementCollectionPublications;
      measurementsPublications();
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {MeasurementCollection}
 */
export const Measurements = new MeasurementCollection();