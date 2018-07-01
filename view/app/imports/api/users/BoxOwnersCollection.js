import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';

/**
 * BoxOwners provides a bi-directional mapping from Box IDs to their Owners.
 * To create a new User, call UserProfiles.define(), which both defines the profile and creates the Meteor.user.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#users}
 */
class BoxOwnersCollection extends BaseCollection {

  constructor() {
    super('BoxOwners', new SimpleSchema({
      username: String,
      boxId: String,
    }));

    this.publicationNames = {
      GET_CURRENT_USER_BOX_OWNERS: 'get_current_user_box_owners',
    };
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
   * Removes all usernames associated with boxId, then adds usernames as owners of boxId.
   * Does not check validity of boxId or usernames, so be careful.
   * @param boxId A boxId.
   * @param usernames An array of usernames.
   */
  updateOwnersForBox(boxId, usernames) {
    this._collection.remove({ boxId });
    usernames.map(username => this.define({ username, boxId }));
  }

  /**
   * Removes all boxes associated with username, then adds username as an owner of the passed boxIDs.
   * Does not check validity of username or boxIDs, so be careful.
   * @param username The username.
   * @param boxIDs The boxIDs that this user now owns.
   */
  updateBoxesWithOwner(username, boxIDs) {
    this._collection.remove({ username });
    boxIDs.map(boxId => this.define({ username, boxId }));
  }

  /**
   * Loads all publications related to this collection.
   */
  publish() {
    if (Meteor.isServer) {
      const self = this;

      // Default publication based on the collection's name - returns all documents in collection.
      Meteor.publish(this.getCollectionName(), function () {
        return self.find();
      });

      Meteor.publish(this.publicationNames.GET_CURRENT_USER_BOX_OWNERS, function () {
        // Publications should check current user with this.userId instead of relying on client-side input.
        const currentUser = Meteor.users.findOne({ _id: this.userId });
        return (currentUser) ? self.find({ username: currentUser.username }) : [];
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 */
export const BoxOwners = new BoxOwnersCollection();
