import { Meteor } from 'meteor/meteor';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import  { Accounts } from 'meteor/accounts-base';
import { Roles } from 'meteor/alanning:roles';
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

    Accounts.onCreateUser((options, userDoc) => {
      if (options.first_name) userDoc.first_name = options.first_name;
      if (options.last_name) userDoc.last_name = options.last_name;
      (options.boxes && options.boxes.length > 0) ? userDoc.boxes = options.boxes : userDoc.boxes = [];
      return userDoc;
    });

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
  define({ email, password, first_name, last_name, boxes = [], role = 'user' }) {
    // const docID = this._collection.insert({ email, password, first_name, last_name, boxes, role });

    // Verify that boxes array contains valid OpqBox ids.
    boxes.forEach(box_id => {
      const box = OpqBoxes.findOne({box_id: box_id});
      if (!box) throw new Meteor.Error(`Boxes contains an invalid box_id: ${box_id}`);
    });

    // Ensure that role is either 'user' or 'admin'.
    if (role !== 'user' || role !== 'admin') {
      throw new Meteor.Error('Invalid user role - must either be "user" or "admin"');
    }

    // Create the user. The username and password fields are required by the Accounts package.
    // The rest are top-level user fields that OPQView will maintain. We attach these fields via Accounts.onCreateUser()
    // which is defined in the constructor of this class. Note that userId is only returned on the server, and so
    // we do not need to do a Meteor.isServer check when we define the user's role (which must only be done on server).
    const userId = Accounts.createUser({
      username: email,
      password: password,
      first_name: first_name,
      last_name: last_name,
      boxes: boxes
    });

    // Set user role.
    // We are using group-based roles; 'opq-view' is the default group and can either be 'user' or 'admin'.
    if (userId) {
      Roles.addUsersToRoles(userId, [role], 'opq-view');
    }
    
    return userId;
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