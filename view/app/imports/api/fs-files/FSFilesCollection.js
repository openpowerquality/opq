import { Meteor } from 'meteor/meteor';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Events } from '../events/EventsCollection';
import { BoxEvents } from '../box-events/BoxEventsCollection';
import { progressBarSetup } from '../../modules/utils';

/**
 * Collection class for the fs.files collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#box_events
 */
class FSFilesCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('fs.files', new SimpleSchema({
      filename: { type: String },
      length: { type: Number },
      chunkSize: { type: Number },
      uploadDate: { type: Date },
      md5: { type: String },
      metadata: { type: Object },
      'metadata.event_id': { type: Number },
      'metadata.box_id': { type: String },
    }));

    this.publicationNames = {
    };
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

  /**
   * Returns an object representing a single fs.file.
   * @param {Object} docID - The Mongo.ObjectID of the fs.files document.
   * @returns {Object} - An object representing a single fs.files document.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const filename = doc.filename;
    const length = doc.length;
    const chunkSize = doc.chunkSize;
    const uploadDate = doc.uploadDate;
    const md5 = doc.md5;
    const metadata = doc.metadata;

    return { filename, length, chunkSize, uploadDate, md5, metadata };
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

      const event = Events.findOne({ event_id: doc.metadata.event_id });
      // Ensure metadata.event_id points to an existing Event document.
      if (!event) {
        problems.push(`FS.Files metadata.event_id does not exist in Events collection: ${doc._id}`);
      }

      // Ensure metadata.event_id and metadata.box_id points to an existing BoxEvent document.
      const boxEvent = BoxEvents.findOne({ event_id: doc.metadata.event_id, box_id: doc.metadata.box_id });
      if (!boxEvent) {
        // eslint-disable-next-line max-len
        problems.push(`FS.Files metadata.event_id and metadata_box_id pair does not exist in the BoxEvents collection: ${doc._id}`);
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
 * @type {FSFilesCollection}
 */
export const FSFiles = new FSFilesCollection();
