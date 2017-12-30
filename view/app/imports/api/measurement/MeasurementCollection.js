import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

class MeasurementsCollection extends BaseCollection {

  /**
   * Creates the Measurements collection.
   */
  constructor() {
    super('Measurement',
        'measurements',
        new SimpleSchema({
          box_id: {type: String},
          timestamp_ms: {type: Number},
          voltage: {type: Number},
          frequency: {type: Number}
        }),
        Meteor.settings.opqRemoteMongoUrl
    );

    this.publicationNames = {
      RECENT_MEASUREMENTS: 'recent_measurements'
    };
  }

  /**
   * Defines a new Measurement document.
   * @param {String} box_id - The OPQBox's id value (not Mongo ID)
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the measurement.
   * @param {Number} voltage - The voltage measurement.
   * @param {Number} frequency - The frequency measurement.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency }) {
    const docID = this._collection.insert({ box_id, timestamp_ms, voltage, frequency });
    return docID;
  }

  /**
   * Returns an object representing a single Measurement.
   * @param {Object} docID - The Mongo.ObjectID of the Measurement.
   * @returns {Object} - An object representing a single Measurement.
   */
  dumpOne(docID) {
    const doc = this.findDoc(docID);
    const box_id = doc.box_id;
    const timestamp_ms = doc.timestamp_ms;
    const voltage = doc.voltage;
    const frequency = doc.frequency;

    return { box_id, timestamp_ms, voltage, frequency }
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
 * @type {MeasurementsCollection}
 */
export const Measurements = new MeasurementsCollection();