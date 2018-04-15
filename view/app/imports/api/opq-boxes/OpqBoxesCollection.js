import SimpleSchema from 'simpl-schema';
import { Meteor } from 'meteor/meteor';
import Moment from 'moment';
import BaseCollection from '../base/BaseCollection.js';
import { Locations } from '../locations/LocationsCollection.js';
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
      location: { type: String, optional: true },
      location_start_time_ms: { type: Number, optional: true },
      location_archive: { type: Array, optional: true },
      'location_archive.$': { type: Object, blackbox: true },
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
   * @param {String} location - A location slug indicating this boxes current location. (optional)
   * @param {Number | String} location_start_time_ms - The timestamp when this box became active at this location.
   *        Any representation legal to Moment() will work. (Optional)
   * @param {Array} location_archive An array of {location,location_start_time_ms} objects. (Optional).
   * @returns The docID of the new or changed OPQBox document, or undefined if invoked on the client side.
   */
  define({ box_id, name, description, unplugged = false, calibration_constant, location, location_start_time_ms,
         location_archive }) {
    if (Meteor.isServer) {
      if (location && !Locations.isLocation(location)) {
        throw new Meteor.Error(`Location ${location} is not a defined location.`);
      }
      // Create or modify the OpqBox document associated with this box_id.
      const fixedArchive = location_archive && this.makeLocationArchive(location_archive);
      const fixedLocationTimestamp = this.getUTCTimestamp(location_start_time_ms);
      this._collection.upsert(
        { box_id },
        { $set: { name, description, calibration_constant, location, unplugged,
            location_start_time_ms: fixedLocationTimestamp,
            location_archive: fixedArchive } },
        );
      const docID = this.findOne({ box_id })._id;
      return docID;
    }
    return undefined;
  }

  /**
   * Returns the UTC millisecond representation of the passed timestamp if possible.
   * If timestamp undefined or not convertible to UTC millisecond format, then returns it unchanged.
   * @param timestamp The timestamp
   * @returns {*} The UTC millisecond format, or the timestamp.
   */
  getUTCTimestamp(timestamp) {
    if (timestamp) {
      const momentTimestamp = Moment(timestamp);
      return (momentTimestamp.isValid()) ? momentTimestamp.valueOf() : timestamp;
      }
    return timestamp;
  }

  /**
   * Returns a new location_archive array structure where location_time_stamp_ms has been passed through Moment so that
   * the settings file can provide more user-friendly versions of the timestamp.
   * @param locationArchive The location_archive array.
   * @returns A new location_archive array in which time_stamp_ms has been converted to UTC milliseconds.
   */
  makeLocationArchive(locationArchive) {
    return locationArchive.map(loc => {  // eslint-disable-line
      if (!Locations.isLocation(loc.location)) {
        throw new Meteor.Error(`Location ${loc.location} is not a defined location.`);
      }
      return { location: loc.location, location_start_time_ms: this.getUTCTimestamp(loc.location_start_time_ms) };
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
