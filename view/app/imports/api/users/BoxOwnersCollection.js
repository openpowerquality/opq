import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';

/**
 * User Profiles (first and last name, role, and username (email).
 * To create a new User, call UserProfiles.define(), which both defines the profile and creates the Meteor.user.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#users
 */
class BoxOwnersCollection extends BaseCollection {

  /**
   * Creates the User Profiles collection.
   */
  constructor() {
    super('BoxOwners', new SimpleSchema({
      username: String,
      boxId: String,
    }));
  }

  /**
   * Defines username as an owner of boxId.
   * If username is already specified as an owner of boxID, that docID is returned.
   * Otherwise a new BoxOwners document is created and its docID is returned.
   * Note that no checking is done to see if username and/or boxId is a valid username or boxId. So, be careful.
   * Only works on the server side.
   * @param {String} username - Must be the user's email address.
   * @param {Number} boxId - The id of the box (an integer).
   * @return The docID for this ownership document.
   */
  // eslint-disable-next-line class-methods-use-this
  define({ username, boxId }) {
    if (Meteor.isServer) {
      const existingDoc = this.findOne(username, boxId);
      if (existingDoc) {
        return existingDoc._id;
      }
      return this._collection.insert({ username, boxId });
    }
    // Return undefined if executed on the client (which shouldn't ever happen.)
    return undefined;
  }

  /**
   * Returns an array of the box documents owned by username.
   * @param username The username.
   * @return { Array } An array of box documents owned by this user.
   */
  findBoxesWithOwner(username) {
    return this._collection.find({ username }).fetch();
  }

  /**
   * Returns a (possibly empty) array of boxIds owned by username.
   * @param username The username
   * @return { Array } An array of boxIds owned by this user.
   */
  findBoxIdsWithOwner(username) {
    const docs = this._collection.find({ username }).fetch();
    return (docs) ? _.map(docs, doc => doc.boxId) : [];
  }

  /**
   * Returns a (possibly empty) array of usernames who own the box.
   * @param boxId The boxId.
   * @return { Array } An array of usernames who own boxId.
   */
  findOwnersWithBoxId(boxId) {
    const docs = this._collection.find({ boxId }).fetch();
    return (docs) ? _.map(docs, doc => doc.username) : [];
  }

  findOne(username, boxId) {
    return this._collection.findOne({ username, boxId });
  }

  /**
   * Removes all of the documents associated with username from this collection.
   * @param username The user (owner of boxes).
   */
  removeBoxesWithOwner(username) {
    this._collection.remove({ username });
  }

  /**
   * Returns an object representing a single BoxOwner document.
   * @param {Object} docID - The Mongo.ObjectID of the BoxOwner.
   * @returns {Object} - An object representing a single BoxOwner document.
   */
  dumpOne(docID) {
    const doc = this.findDoc(docID);
    const username = doc.username;
    const boxId = doc.boxId;
    return { username, boxId };
  }


}

/**
 * Provides the singleton instance of this class.
 */
export const BoxOwners = new BoxOwnersCollection();
