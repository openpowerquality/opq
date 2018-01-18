import { Mongo } from 'meteor/mongo';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { progressBarSetup } from '../../modules/utils';

class TrendsCollection extends BaseCollection {

  /**
   * Creates the Trends collection.
   */
  constructor() {
    super('trends', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      box_id: { type: String },
      timestamp_ms: { type: Number },
      voltage: { type: Object },
      'voltage.min': { type: Number, decimal: true },
      'voltage.max': { type: Number, decimal: true },
      'voltage.average': { type: Number, decimal: true },
      frequency: { type: Object },
      'frequency.min': { type: Number, decimal: true },
      'frequency.max': { type: Number, decimal: true },
      'frequency.average': { type: Number, decimal: true },
      thd: { type: Object, optional: true },
      'thd.min': { type: Number, decimal: true },
      'thd.max': { type: Number, decimal: true },
      'thd.average': { type: Number, decimal: true },
    }));

    this.publicationNames = {
    };
  }

  /**
   * Defines a new Trends document.
   * @param {String} box_id - The OPQBox's id value (not Mongo ID)
   * @param {Number} timestamp_ms - The unix timestamp (millis) of the trend.
   * @param {Number} voltage - The voltage trend object.
   * @param {Number} frequency - The frequency trend object.
   * @param {Number} thd - The thd trend object.
   * @returns The newly created document ID.
   */
  define({ box_id, timestamp_ms, voltage, frequency, thd }) {
    const docID = this._collection.insert({ box_id, timestamp_ms, voltage, frequency, thd });
    return docID;
  }

  /**
   * Returns an object representing a single Trend.
   * @param {Object} docID - The Mongo.ObjectID of the Trend.
   * @returns {Object} - An object representing a single Trend.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const box_id = doc.box_id;
    const timestamp_ms = doc.timestamp_ms;
    const voltage = doc.voltage;
    const frequency = doc.frequency;
    const thd = doc.thd;

    return { box_id, timestamp_ms, voltage, frequency, thd };
    /* eslint-enable camelcase */
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('trendsIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    // Get all OpqBox IDs.
    const boxIDs = OpqBoxes.find().map(doc => doc.box_id);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`Trends document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();

      // Ensure box_id of the trend exists in opq_boxes collection.
      if (!boxIDs.includes(doc.box_id)) {
        problems.push(`Trends box_id does not exist in opq_boxes collection: ${doc.box_id} (docID: ${doc._id})`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to the Trends collection.
   */
  publish() { // eslint-disable-line class-methods-use-this
    // if (Meteor.isServer) {
    //
    // }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {TrendsCollection}
 */
export const Trends = new TrendsCollection();
