import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

/**
 * This collection is internal to GridFS and is used for storing file chunks.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#fschunks}
 */
class FSChunksCollection extends BaseCollection {

  constructor() {
    super('fs.chunks', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
      files_id: { type: Mongo.ObjectID },
      n: Number,
      data: Uint8Array,
    }));
  }

  /**
   * Defines a new fs.chunks document.
   * @param {ObjectID} files_id - The ObjectID of the corresponding fs.files document.
   * @param {Number} n - The number of chunks.
   * @param {Object} data - The binary for this chunk.
   * @returns The newly created document ID.
   */
  define({ files_id, n, data }) {
    const docID = this._collection.insert({ files_id, n, data });
    return docID;
  }

  /** Publications for this collection are disabled. */
  publish() { }
}

/**
 * Provides the singleton instance of this class.
 * @type {FSChunksCollection}
 */
export const FSChunks = new FSChunksCollection();
