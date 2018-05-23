import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

/**
 * FSFiles is internal to GridFS and stores file metadata.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#fsfiles}
 */
class FSFilesCollection extends BaseCollection {

  constructor() {
    super('fs.files', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      filename: String,
      length: { type: Number },
      chunkSize: { type: Number },
      uploadDate: { type: Date },
      md5: { type: String },
      metadata: { type: Object },
      'metadata.event_id': { type: Number },
      'metadata.box_id': { type: String },
    }));
  }

  /**
   * Defines a new fs.files document.
   * @param {String} filename - The filename, which corresponds to box_event's data_fs_filename field.
   * @param {Number} length - The size of data.
   * @param {Number} chunkSize - The max size of chunks.
   * @param {Number} uploadDate - The creation date.
   * @param {String} md5 - The file md5.
   * @param {Object} metadata - Object that holds the event's event_id and box_id.
   * @returns The newly created document ID.
   */
  define({ filename, length, chunkSize, uploadDate, md5, metadata }) {
    const docID = this._collection.insert({ filename, length, chunkSize, uploadDate, md5, metadata });
    return docID;
  }

  /** Publications for this collection are disabled. */
  publish() { }
}

/**
 * Provides the singleton instance of this class.
 * @type {FSFilesCollection}
 */
export const FSFiles = new FSFilesCollection();
