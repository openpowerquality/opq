import { Meteor } from 'meteor/meteor';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Accounts } from 'meteor/accounts-base';
import { Roles } from 'meteor/alanning:roles';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/**
 * Collection class for the users collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#users
 */
class UsersCollection {

  /**
   * Note that since the Accounts package manages the Users collection, we aren't actually using BaseCollection.
   * This class serves as a wrapper around the Accounts package.
   */
  constructor() {
    this._collection = Meteor.users;
    this._collectionName = 'users';

    if (Meteor.isServer) {
      Accounts.onCreateUser((options, userDoc) => {
        const modifiedUserDoc = Object.assign({}, userDoc); // Clone userDoc so we don't mutate it directly.
        if (options.first_name) modifiedUserDoc.first_name = options.first_name;
        if (options.last_name) modifiedUserDoc.last_name = options.last_name;
        modifiedUserDoc.boxes = (options.boxes && options.boxes.length > 0) ? options.boxes : [];
        return modifiedUserDoc;
      });
    }

    this.publicationNames = {

    };
  }

  /**
   * Defines a new User document. Note: Do not use this for client-side user signup. We will eventually refactor
   * this so that only admins can create new users.
   * @param {String} email - The user's email address. Acts as user name.
   * @param {String} password - The user's password.
   * @param {String} first_name - The user's first name.
   * @param {String} last_name - The user's last name.
   * @param {[Number]} boxes - The OPQBoxes this user has acccess to.
   * @param {String} role - The role of the user.
   */
  // eslint-disable-next-line class-methods-use-this
  define({ email, password, first_name, last_name, boxes = [], role = 'user' }) {
    if (Meteor.isServer) {
      // Verify that boxes array contains valid OpqBox ids.
      boxes.forEach(boxId => {
        const box = OpqBoxes.findOne({ box_id: boxId });
        if (!box) throw new Meteor.Error(`Boxes contains an invalid box_id: ${boxId}`);
      });

      // Ensure that role is either 'user' or 'admin'.
      if (role !== 'user' && role !== 'admin') {
        throw new Meteor.Error('Invalid user role - must either be "user" or "admin"');
      }

      // Create the user. The username and password fields are required by the Accounts package.
      // The rest are top-level user fields that OPQView will maintain. We attach these fields via
      // Accounts.onCreateUser() which is defined in the constructor of this class. Note that userId is only returned
      // on the server, and so we do not need to do a Meteor.isServer check when we define the user's
      // role (which must only be done on server).
      const userId = Accounts.createUser({
        email: email,
        password: password,
        first_name: first_name,
        last_name: last_name,
        boxes: boxes,
      });

      // Set user role.
      // We are using group-based roles; 'opq-view' is the default group used for general-purpose app permissions.
      if (userId) {
        Roles.addUsersToRoles(userId, [role], 'opq-view');
      }

      return userId;
    }

    return null;
  }

  /**
   * Returns an object representing a single User.
   * @param {Object} docID - The Mongo.ObjectID of the User.
   * @returns {Object} - An object representing a single User.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const email = doc.email;
    const password = doc.password;
    const first_name = doc.first_name;
    const last_name = doc.last_name;
    const boxes = doc.boxes;
    const role = doc.roles;

    return { email, password, first_name, last_name, boxes, role };
    /* eslint-enable camelcase */
  }

  /**
   * Loads all publications related to this collection.
   * Note: We conditionally import the publications file only on the server as a way to hide publication code from
   * being sent to the client.
   */
  publish() { // eslint-disable-line class-methods-use-this
    if (Meteor.isServer) { // eslint-disable-line no-empty
    }
  }

  /**
   * Calls the MongoDB native find() on this collection.
   * @see {@link http://docs.meteor.com/api/collections.html#Mongo-Collection-find|Meteor Docs Mongo.Collection.find()}
   * @param {Object} selector - A MongoDB selector object.
   * @param {Object} options - A MongoDB options object.
   * @returns {Cursor} - The MongoDB cursor containing the results of the query.
   */
  find(selector = {}, options = {}) {
    return this._collection.find(selector, options);
  }

  /**
   * Calls the MongoDB native findOne() on this collection.
   * @see {@link http://docs.meteor.com/api/collections.html#Mongo-Collection-findOne|
   * Meteor Docs Mongo.Collection.findOne()}
   * @param {Object} selector - A MongoDB selector object.
   * @param {Object} options - A MongoDB options object.
   * @returns {Object} - The document containing the results of the query.
   */
  findOne(selector = {}, options = {}) {
    return this._collection.findOne(selector, options);
  }

  updateUser(userID, userObj) {
    // Meteor method takes care of user auth, so should be safe at this point.
    return this._collection.update({ _id: userID }, { $set: userObj });
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {UsersCollection}
 */
export const Users = new UsersCollection();
