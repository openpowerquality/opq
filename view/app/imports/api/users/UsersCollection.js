import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';

/**
 * Collection class for the users collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#users
 */
class UsersCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('OpqBoxes',
        'opq_boxes',
        new SimpleSchema({
          email: {type: String},
          password: {type: String},
          first_name: {type: String},
          last_name: {type: String},
          boxes: {type: [Number]}, // Array of box_id's
          role: {type: String}
        })
    );

    this.publicationNames = {

    };
  }

  /**
   * Defines a new User document.
   * @param {String} email - The user's email address. Acts as user name.
   * @param {String} password - The user's password.
   * @param {String} first_name - The user's first name.
   * @param {String} last_name - The user's last name.
   * @param {[Number]} boxes - The OPQBoxes this user has acccess to.
   * @param {String} role - The role of the user.
   */
  define({ email, password, first_name, last_name, boxes, role }) {
    const docID = this._collection.insert({ email, password, first_name, last_name, boxes, role });
    return docID;
  }

  /**
   * Returns an object representing a single User.
   * @param {Object} docID - The Mongo.ObjectID of the User.
   * @returns {Object} - An object representing a single User.
   */
  dumpOne(docID) {
    const doc = this.findDoc(docID);
    const email = doc.email;
    const password = doc.password;
    const first_name = doc.first_name;
    const last_name = doc.last_name;
    const boxes = doc.boxes;
    const role = doc.roles;

    return { email, password, first_name, last_name, boxes, role }
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
 * @type {UsersCollection}
 */
export const UsersCollection = new UsersCollection();