import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import BaseCollection from '../base/BaseCollection.js';
import { FSFiles } from '../fs-files/FSFilesCollection';
import { progressBarSetup } from '../../modules/utils';

/**
 * Collection class for the fs.chunks collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#box_events
 */
class FSChunksCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('fs.chunks', new SimpleSchema({
      files_id: { type: Mongo.ObjectID },
      n: { type: Number },
      data: { type: Object, blackbox: true },
    }));

    this.publicationNames = {
    };
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

  /**
   * Returns an object representing a single fs.chunk.
   * @param {Object} docID - The Mongo.ObjectID of the fs.chunk document.
   * @returns {Object} - An object representing a single fs.chunk document.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const files_id = doc.files_id;
    const n = doc.n;
    const data = doc.data;

    return { files_id, n, data };
    /* eslint-enable camelcase */
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('fsFilesIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid) {
        // eslint-disable-next-line max-len
        problems.push(`FS.Files document failed schema validation: ${doc._id} (Invalid keys: ${validationContext.invalidKeys()})`);
      }
      validationContext.resetValidation();

      // Ensure files_id points to valid fs.files document.
      const fsFile = FSFiles.findOne({ _id: doc.files_id });
      if (!fsFile) {
        problems.push(`FS.Chunks files_id does match an existing FS.Files document: ${doc._id}`);
      }
    });

    pb.clearInterval();
    return problems;
  }

  /**
   * Loads all publications related to this collection.
   */
  publish() { // eslint-disable-line class-methods-use-this
    if (Meteor.isServer) { // eslint-disable-line no-empty
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {FSChunksCollection}
 */
export const FSChunks = new FSChunksCollection();
