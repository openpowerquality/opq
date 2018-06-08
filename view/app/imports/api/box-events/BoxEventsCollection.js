import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { FSFiles } from '../fs-files/FSFilesCollection';
import { FSChunks } from '../fs-chunks/FSChunksCollection';

/**
 * BoxEvents provides event meta-data for a given OPQ Box.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#box-events}
 */
class BoxEventsCollection extends BaseCollection {

  constructor() {
    super('box_events', new SimpleSchema({
      event_id: Number,
      box_id: String,
      event_start_timestamp_ms: Number,
      event_end_timestamp_ms: Number,
      window_timestamps_ms: [Number], // For research purposes.
      thd: Number,
      itic: String,
      location: { type: Object, optional: true },
      'location.start_time': { type: Number, optional: true },
      'location.zipcode': { type: Number, optional: true },
      data_fs_filename: String, // Stores the GridFs filename. Format is 'event_eventNumber_boxId'
    }));

    this.publicationNames = {
      EVENT_DATA: 'event_data',
    };
    if (Meteor.server) {
      this._collection.rawCollection().createIndex({ event_start_timestamp_ms: 1, box_id: 1 }, { background: true });
    }
  }

  /**
   * Defines a new BoxEvent document.
   * @param {Number} event_id - The event_id associated with the BoxEvent.
   * @param {String} box_id - The box_id associated with the BoxEvent.
   * @param {Number} event_start - The start timestamp (unix milliseconds) of the event.
   * @param {Number} event_end - The end timestamp (unix milliseconds) of the event.
   * @param {[Number]} window_timestamps - An array of timestamps, for research purposes. See docs for details.
   * @param {Number} thd - The total harmonic distortion value of the event.
   * @param {String} itic - The ITIC value of the event.
   * @param {Object} location - The location of the OPQBox at the time of the event.
   * @param {String} data_fs_filename - The GridFS filename holding the actual event waveform data.
   * @returns The newly created document ID.
   */
  define({ event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename }) {
    const docID = this._collection.insert({
      event_id, box_id, event_start, event_end, window_timestamps, thd, itic, location, data_fs_filename,
    });
    return docID;
  }

  /**
   * Checks the integrity of the passed Box_Event document. The checks include:
   *   * Is the event_id associated with a known Event?
   *   * Is the box_id associated with a known Box?
   *   * Are event_start and event_end reasonable unix millisecond timestamps?
   *   * Does data_fs_filename specify a valid document in the FS.Files collection?
   * Note we are not checking for a valid Location yet.
   * @param doc The box_event document.
   * @param repair If repair is true, and an integrity problem is discovered, then this Box_Event and the
   * corresponding FSFile and FSChunk are deleted.
   * @returns {Array} An array of strings describing any problems that were found.
   */
  checkIntegrity(doc, repair) {
    const problems = [];
    if (!Events.isEventId(doc.event_id)) {
      problems.push(`event_id ${doc.event_id} (invalid)`);
    }
    if (!OpqBoxes.isBoxId(doc.box_id)) {
      problems.push(`box_id ${doc.box_id} (invalid)`);
    }
    // Don't check for valid location yet.
    // if (!Locations.isLocation(doc.location)) {
    //   problems.push(`location ${doc.location} (invalid)`);
    // }
    if (!FSFiles.isFilename(doc.data_fs_filename)) {
      problems.push(`data_fs_filename ${doc.data_fs_filename} (invalid)`);
    }
    if (!this.isValidTimestamp(doc.event_start_timestamp_ms)) {
      problems.push(`event_start_timestamp_ms ${doc.event_start_timestamp_ms} (invalid)`);
    }
    if (!this.isValidTimestamp(doc.event_end_timestamp_ms)) {
      problems.push(`event_end_timestamp_ms ${doc.event_end_timestamp_ms} (invalid)`);
    }
    const result = { docName: `Box_Event ${doc.event_id}, ${doc.box_id}`, problems };
    if (repair) {
      result.repair = this.repair(doc);
    }
    return result;
  }

  /**
   * Repair (i.e. delete) a Box_Event. Also deletes the associated fs.file, and fs.chunks (if FS filename is valid).
   * @param doc The box_event document.
   * @return A string indicating how many fs.files, and fs.chunks were deleted in addition to the box_event.
   */
  repair(doc) {
    let returnString = '';
    const filename = doc.data_fs_filename;
    if (FSFiles.isFilename(filename)) {
      const files_id = FSFiles._collection.findOne({ filename })._id;
      const fsFileChunkDocs = FSChunks.find({ files_id }).fetch();
      const fsChunkIDs = _.pluck(fsFileChunkDocs, '_id');
      returnString += `Deleting FSFile ${files_id}, ${fsChunkIDs.length} FSChunks, and `;
      FSFiles._collection.remove({ filename });
      FSChunks._collection.remove({ _id: { $in: fsChunkIDs } });
    }
    returnString += `box_event ${doc._id}`;
    this._collection.remove({ _id: doc._id });
    return returnString;
  }

  /** Publications for this collection are disabled. */
  publish() { }
}

/**
 * Provides the singleton instance of this class.
 * @type {BoxEventsCollection}
 */
export const BoxEvents = new BoxEventsCollection();
