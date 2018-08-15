import { Meteor } from 'meteor/meteor';
import { Accounts } from 'meteor/accounts-base';
import { Roles } from 'meteor/alanning:roles';
import { _ } from 'underscore';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';
import { BoxOwners } from './BoxOwnersCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { ROLE } from '../opq/Role';

/**
 * User Profiles (first and last name, role, and username (email).
 * To create a new User, call UserProfiles.define(), which both defines the profile and creates the Meteor.user.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#users}
 */
class UserProfilesCollection extends BaseCollection {

  constructor() {
    super('UserProfiles', new SimpleSchema({
      username: String,
      firstName: String,
      lastName: String,
      role: String,
      phone: { type: String, optional: true },
      notification_preferences: { type: Object, optional: true },
      'notification_preferences.text': { type: Boolean, optional: true },
      'notification_preferences.email': { type: Boolean, optional: true },
      'notification_preferences.max_per_day': { type: String, optional: true },
      'notification_preferences.notification_types': { type: Array, optional: true },
        'notification_preferences.notification_types.$': { type: String, blackbox: true },
    }));
  }

  /**
   * Defines a new UserProfile if username is not defined in Meteor.users, and adds the user to Meteor.users.
   * Updates an existing User Profile if username is already defined in Meteor.users.
   * @param {String} username - Must be the user's email address.
   * @param {String} password - The user's password. (Only used when adding a user to Meteor.users.)
   * @param {String} firstName - The user's first name.
   * @param {String} lastName - The user's last name.
   * @param {String} role - The role of the user: either 'admin' or 'user'.
   * @param {[Number]} boxIds - An array of Strings containing the IDs of the boxes that can be managed by this user.
   * @param {String} phone - The user's phone number concatenated with user's provider.
   * @param {String} notification_preferences - The user's preferences on how they are notified
   * and which notification types they want to receive.
   */
  // eslint-disable-next-line class-methods-use-this
  define({ username, password, firstName, lastName, boxIds = [], role = 'user',
           phone, notification_preferences }) {
    if (Meteor.isServer) {

      OpqBoxes.assertValidBoxIds(boxIds);

      // Role must be either 'user' or 'admin'.
      if (role !== ROLE.USER && role !== ROLE.ADMIN) {
        throw new Meteor.Error('Invalid user role - must either be "user" or "admin"');
      }

      // Figure out if the user is already defined in Meteor Accounts.
      let user = Accounts.findUserByUsername(username);
      let userId = user && user._id;
      // Define the new user in Meteor Accounts if necessary.
      if (!userId) {
        userId = Accounts.createUser({ username, email: username, password });
        user = Accounts.findUserByUsername(username);
      }

      // Create or modify the UserProfiles document associated with this username.
      this._collection.upsert({ username }, {
        $set: {
          firstName,
          lastName,
          role,
          phone,
          notification_preferences,
        },
      });
      const profileId = this.findOne({ username })._id;

      // Set the role using the Roles package. This makes it easier to do Role-based decisions on client.
      if (userId) {
        Roles.addUsersToRoles(userId, role);
      }

      // Remove any current box ownerships, add new ownerships as specified in boxIds.
      this._updateBoxIds(username, boxIds);

      // Return the profileID if executed on the server.
      return profileId;
    }
    // Return undefined if executed on the client.
    return undefined;
  }

  /**
   * Internal method to perform updating of the BoxOwnersCollection with a new set of box ownerships for this user.
   * @param boxIds An array containing the new list of box ownership.
   * @private
   */
  _updateBoxIds(username, boxIds) {
    // Remove any current box ownerships, add new ownerships as specified in boxIds.
    BoxOwners.removeBoxesWithOwner(username);
    boxIds.map(boxId => BoxOwners.define({ username, boxId }));
  }

  /**
   * Returns the profile document corresponding to username, or throws error if not found.
   * @param username
   * @returns {Object} The profile document.
   * @throws { Meteor.Error } If the profile document does not exist for this username.
   */
  findByUsername(username) {
    const profile = this._collection.findOne({ username });
    if (profile) {
      return profile;
    }
    throw new Meteor.Error(`Could not find profile corresponding to ${username}`);
  }


  /**
   * Returns the profile document corresponding to id, or throws error if not found.
   * @param id
   * @returns {Object} The profile document.
   * @throws { Meteor.Error } If the profile document does not exist for this id.
   */
  findByID(userID) {
    const id = new Meteor.Collection.ObjectID(userID);
    const profile = this._collection.findOne({ _id: id }, {});
    if (profile) {
      return profile;
    }
    throw new Meteor.Error(`Could not find profile corresponding to ${id}`);
  }

  /**
   * Returns a list of all of the currently defined usernames.
   * @param sort If truthy, then sort the list before returning.
   * @returns {*} A list of strings, each one corresponding to a username.
   */
  findUsernames(sort = false) {
    const docs = this._collection.find({}).fetch();
    const usernames = _.pluck(docs, 'username');
    return (sort) ? _.sortBy(usernames, username => username.toLowerCase()) : usernames;
  }

  /**
   * Updates the User Profile (firstName, lastName, boxIds).
   * Runs on server side only. Only admins should update the user profile to control box ownership.
   * @param id Must be a valid UserProfile docID.
   * @param args An object containing fields that can be updated: firstName, lastName, and boxIDs.
   * @throws { Meteor.Error } If docID is not defined or any of the boxIds are not defined.
   * @returns An object containing the updated fields.
   */
  update(docID, args) {
    if (Meteor.isServer) {
      const userProfileDoc = this.assertIsDefined(docID);
      const updateData = {};
      if (args.firstName) {
        updateData.firstName = args.firstName;
      }
      if (args.lastName) {
        updateData.lastName = args.lastName;
      }
      if (args.boxIds) {
        OpqBoxes.assertValidBoxIds(args.boxIds);
        this._updateBoxIds(userProfileDoc.username, args.boxIds);
      }
      if (args.phone) {
        updateData.phone = args.phone;
      }
      if (args.notification_preferences) {
        updateData.notification_preferences = args.notification_preferences;
      }
      this._collection.update(docID, { $set: updateData });
      return updateData;
    }
    return undefined;
  }

  /**
   * Removes the user from Meteor.users and from UserProfiles.
   * If docID does not exist, then returns false.
   * Will only work on the server-side.
   * @param docID A docID
   * @returns True if the docID exists and was deleted, false otherwise.
   */
  remove(docID) {
    if (Meteor.isServer) {
      const profile = this.findOne(docID);
      if (profile) {
        this._collection.remove(docID);
        const user = Accounts.findUserByUsername(profile.username);
        if (user) {
          Meteor.users.remove(user._id);
        }
        return true;
      }
      return false;
    }
    return undefined;
  }

  /**
   * Removes all UserProfiles and associated Meteor.users.
   * This is implemented by mapping through all elements because mini-mongo does not implement the remove operation.
   * Will only work on the server side.
   * removeAll should only used for testing purposes, so it doesn't need to be efficient.
   * @returns true
   */
  removeAll() {
    if (Meteor.isServer) {
      const userProfiles = this._collection.find().fetch();
      const instance = this;
      _.forEach(userProfiles, (profile) => instance.remove(profile.username));
    }
    return true;
  }

  /**
   * Checks user's preferred way of receiving notifications and returns array of email addresses
   * Notifications can be received through text message and email
   * @param user {Object}
   * @returns {Array}
   */
  getRecipients(user) {
    const recipients = [];
    if (user.notification_preferences.text === true && user.phone !== undefined) {
      recipients.push(user.phone);
    }
    if (user.notification_preferences.email === true) {
      recipients.push(user.username);
    }
    return recipients;
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {UserProfilesCollection}
 */
export const UserProfiles = new UserProfilesCollection();
