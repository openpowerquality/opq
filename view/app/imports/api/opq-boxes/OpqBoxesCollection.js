import SimpleSchema from 'simpl-schema';
import { Meteor } from 'meteor/meteor';
import Moment from 'moment';
import BaseCollection from '../base/BaseCollection.js';
import { BoxOwners } from '../users/BoxOwnersCollection';
import { Locations } from '../locations/LocationsCollection.js';

/**
 * Provides information about each OPQ Box in the system
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#opqboxes}
 */
class OpqBoxesCollection extends BaseCollection {

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

    this.publicationNames = {
      GET_OPQ_BOXES: 'get_opq_boxes',
      GET_CURRENT_USER_OPQ_BOXES: 'get_current_user_opq_boxes',
    };
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

  /**
   * Loads all publications related to this collection.
   */
  publish() {
    if (Meteor.isServer) {
      const self = this;

      Meteor.publish(this.publicationNames.GET_OPQ_BOXES, function () {
        // check(startTime, Match.Maybe(Number));
        // check(endTime, Match.Maybe(Number));
        const opqBoxes = self.find({});
        return opqBoxes;
      });

      Meteor.publish(this.publicationNames.GET_CURRENT_USER_OPQ_BOXES, function () {
        // Publications should check current user with this.userId instead of relying on client-side input.
        const currentUser = Meteor.users.findOne({ _id: this.userId });
        if (currentUser) {
          const boxIds = BoxOwners.findBoxIdsWithOwner(currentUser.username);
          return self.find({ box_id: { $in: boxIds } });
        }
        return [];
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {OpqBoxesCollection}
 */
export const OpqBoxes = new OpqBoxesCollection();
