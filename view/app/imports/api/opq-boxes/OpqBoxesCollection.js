import SimpleSchema from 'simpl-schema';
import { Meteor } from 'meteor/meteor';
import Moment from 'moment';
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
      box_id: String,
      name: { type: String, optional: true },
      description: { type: String, optional: true },
      unplugged: { type: Boolean, optional: true },
      calibration_constant: Number,
      locations: { type: Array },
      'locations.$': { type: Object, blackbox: true },
    }));
  }

  /**
   * Defines a new OpqBox document.
   * Only works on server side.
   * Updates info associated with box_id if it is already defined.
   * @param {String} box_id - The unique identification value of the OPQBox.
   * @param {String} name - The unique user-friendly name of the OPQBox.
   * @param {String} description - The (optional) description of the OPQBox.
   * @param {Boolean} unplugged - True if the box is not attached to an outlet. Default: false (plugged in)
   * @param {Number} calibration_constant - The calibration constant value of the box. See docs for details.
   * @param {[Object]} locations - The history of locations of the OPQBox.
   * @returns The docID of the new or changed OPQBox document, or undefined if invoked on the client side.
   */
  define({ box_id, name, description, calibration_constant, locations, unplugged = false }) {
    if (Meteor.isServer) {
      // Create or modify the OpqBox document associated with this box_id.
      const newLocs = this.makeLocationArray(locations);
      this._collection.upsert(
        { box_id },
        { $set: { name, description, calibration_constant, locations: newLocs, unplugged } },
        );
      const docID = this.findOne({ box_id })._id;
      return docID;
    }
    return undefined;
  }

  /**
   * Returns a new locations array structure where time_stamp_ms has been passed through Moment so that
   * the settings file can provide more user-friendly versions of the timestamp.
   * @param locations The locations array.
   * @returns A new locations array in which time_stamp_ms has been converted to UTC milliseconds.
   */
  makeLocationArray(locations) {
    return locations.map(location => {
      const momentTimestamp = Moment(location.time_stamp_ms);
      if (momentTimestamp.isValid()) {
        location.time_stamp_ms = momentTimestamp.valueOf(); // eslint-disable-line
      }
      return location;
    });
  }

  /**
   * Returns the box document associated with box_id.
   * Throws an error if no box document was found for the passed box_id.
   * @param box_id The box ID.
   * @returns {any} The box document.
   */
  findBox(box_id) {
    const boxDoc = this._collection.findOne({ box_id });
    if (boxDoc) {
      return boxDoc;
    }
    throw new Meteor.Error(`No box found with id: ${box_id}`);
  }

  /**
   * Returns the boxIDs of all boxes in the collection.
   * @return { Array } An array of boxIds.
   */
  findBoxIds() {
    const docs = this._collection.find({}).fetch();
    return (docs) ? _.map(docs, doc => doc.box_id) : [];
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
}

/**
 * Provides the singleton instance of this class.
 * @type {OpqBoxesCollection}
 */
export const OpqBoxes = new OpqBoxesCollection();
