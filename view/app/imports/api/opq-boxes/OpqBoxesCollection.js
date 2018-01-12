import { Meteor } from 'meteor/meteor';
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
    super('opq_boxes',
        new SimpleSchema({
          box_id: {type: String},
          name: {type: String},
          description: {type: String, optional: true},
          calibration_constant: {type: Number},
          locations: {type: [Object]}
        })
    );

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
    const doc = this.findDoc(docID);
    const box_id = doc.box_id;
    const name = doc.name;
    const description = doc.description;
    const calibration_constant = doc.calibration_constant;
    const locations = doc.locations;

    return { box_id, name, description, calibration_constant, locations }
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
      if (!validationContext.isValid) {
        problems.push(`OpqBox document failed schema validation: ${doc._id} (Invalid keys: ${validationContext.invalidKeys()})`);
      }
      validationContext.resetValidation();

      // Ensure box_id field is unique
      if (this.find({box_id: doc.box_id}).count() > 1) problems.push(`OpqBox box_id is not unique: ${doc.box_id}`);

      // Ensure name field is unique
      if (this.find({name: doc.name}).count() > 1) problems.push(`OpqBox name is not unique: ${doc.name}`);
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to this collection.
   */
  publish() {

  }
}

/**
 * Provides the singleton instance of this class.
 * @type {OpqBoxesCollection}
 */
export const OpqBoxes = new OpqBoxesCollection();