import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { progressBarSetup } from '../../modules/utils';

/**
 * Collection class for the opq_boxes collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#opq_boxes
 */
class OpqBoxesCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('opq_boxes', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      box_id: { type: String },
      name: { type: String, optional: true },
      description: { type: String, optional: true },
      calibration_constant: Number,
      locations: { type: Array },
      'locations.$': Object,
    }));

    this.publicationNames = {

    };
  }

  /**
   * Defines a new OpqBox document.
   * @param {String} box_id - The unique identification value of the OPQBox.
   * @param {String} name - The unique user-friendly name of the OPQBox.
   * @param {String} description - The (optional) description of the OPQBox.
   * @param {Number} calibration_constant - The calibration constant value of the box. See docs for details.
   * @param {[Object]} locations - The history of locations of the OPQBox.
   */
  define({ box_id, name, description, calibration_constant, locations }) {
    const docID = this._collection.insert({ box_id, name, description, calibration_constant, locations });
    return docID;
  }

  /**
   * Returns an object representing a single OpqBox.
   * @param {Object} docID - The Mongo.ObjectID of the OpqBox.
   * @returns {Object} - An object representing a single OpqBox.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const box_id = doc.box_id;
    const name = doc.name;
    const description = doc.description;
    const calibration_constant = doc.calibration_constant;
    const locations = doc.locations;

    return { box_id, name, description, calibration_constant, locations };
    /* eslint-enable camelcase */
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('opqBoxesIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`OpqBox document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();

      // Ensure box_id field is unique
      if (this.find({ box_id: doc.box_id }).count() > 1) problems.push(`OpqBox box_id is not unique: ${doc.box_id}`);

      // Ensure name field is unique (not counting an unset name - represented by empty strings)
      // eslint-disable-next-line max-len
      if (doc.name && this.find({ name: doc.name }).count() > 1) problems.push(`OpqBox name is not unique: ${doc.name}`);
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to this collection.
   */
  publish() { // eslint-disable-line class-methods-use-this

  }
}

/**
 * Provides the singleton instance of this class.
 * @type {OpqBoxesCollection}
 */
export const OpqBoxes = new OpqBoxesCollection();
