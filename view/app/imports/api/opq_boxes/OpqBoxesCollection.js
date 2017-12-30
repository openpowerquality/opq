import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

/**
 * Collection class for the opq_boxes collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#opq_boxes
 */
class OpqBoxesCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('OpqBoxes',
        'opq_boxes',
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
 * @type {OpqBoxesCollection}
 */
export const OpqBoxesCollection = new OpqBoxesCollection();