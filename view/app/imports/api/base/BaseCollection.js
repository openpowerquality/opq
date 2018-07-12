import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import _ from 'lodash';
import moment from 'moment';
import { Roles } from 'meteor/alanning:roles';
import { ROLE } from '../opq/Role';

/**
 * BaseCollection is an abstract superclass of all other collection classes.
 */
class BaseCollection {

  /**
   * Superclass constructor for all collections.
   * Defines internal fields required by all collections.
   * @param {String} collectionName - The name of the collection.
   * @param {Object} schema - The SimpleSchema instance that defines this collection's schema.
   */
  constructor(collectionName, schema) {
    if (typeof collectionName !== 'string') throw new Meteor.Error('collectionName must be a String.');
    if (!(schema instanceof SimpleSchema)) throw new Meteor.Error('schema must be a SimpleSchema instance.');

    this._collectionName = collectionName;
    this._schema = schema;
    this._collection = new Mongo.Collection(collectionName, { idGeneration: 'MONGO' });
    this._collection.attachSchema(schema);
    this._earliest_timestamp_ms = moment('2017-01-01').valueOf();
  }

  /**
   * Returns true if timestamp_ms is valid (i.e. represents a timestamp after 2016.
   * @param timestamp_ms A timestamp.
   * @returns {boolean} True if the timestamp represents a time in 2017 or later.
   */
  isValidTimestamp(timestamp_ms) {
    return (timestamp_ms > this._earliest_timestamp_ms);
  }

  /**
   * Returns the schema (SimpleSchema) associated with this collection.
   * @returns {SimpleSchema} - The SimpleSchema instance.
   */
  getSchema() {
    return this._schema;
  }

  /**
   * Returns the number of documents in this collection.
   * @returns {Number} - The number of documents in the collection.
   */
  count() {
    return this._collection.find().count();
  }

  /**
   * Returns the number of documents in this collection with a UTC millisecond timestamp greater than today's
   * date at midnight.
   * @param timeField The name of the field containing a timestamp in UTC millisecond format.
   * @returns The number of documents whose timestamp is from today.
   */
  countToday(timeField) {
    const startToday = moment().startOf('day').valueOf();
    const query = {};
    query[timeField] = { $gte: startToday };
    return this._collection.find(query).count();

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

  /**
   * Returns true if the passed entity is in this collection.
   * @param { id } id The docID.
   * @returns Truthy (the document) if docID is in the collection, false (null) otherwise.
   */
  isDefined(id) {
    return this._collection.findOne({ _id: id });
  }

  /** Default update method throws an error. All subclasses must write their own so they can validate arguments. */
  update(id, args) {
    throw new Meteor.Error(`BaseCollection.update() method called with id ${id} and args ${args}.`);
  }

  /**
   * Default publication of collection (publishes entire collection). Derived classes will often override with
   * their own publish() method, as its generally a bad idea to publish the entire collection to the client.
   */
  publish() {
    if (Meteor.isServer) {
      Meteor.publish(this._collectionName, () => this._collection.find());
    }
  }

  /**
   * Default version of getPublicationName returns the single publication name.
   * Derived classes many need to override this method as well.
   * @returns The default publication name.
   */
  getPublicationName() {
    return this._collectionName;
  }

  /**
   * Returns the collection name.
   * @return {string} The collection name as a string.
   */
  getCollectionName() {
    return this._collectionName;
  }

  /**
   * Default subscription method for entities.
   * It subscribes to the entire collection.
   * This is generally useful only during testing.
   */
  subscribe() {
    if (Meteor.isClient) {
      Meteor.subscribe(this._collectionName);
    }
  }

  /**
   * Finds and returns the entire document of the given docID.
   * @param {Object} docID - The Mongo.ObjectID of the document to find.
   * @returns {Object} - The found document.
   */
  findDoc(docID) {
    const doc = this.findOne({ _id: docID }, {});
    if (!doc) {
      throw new Meteor.Error(`Could not find document with docID: ${docID} in collection: ${this._collectionName}.`);
    }
    return doc;
  }

  /**
   * Removes all elements of this collection.
   * This is implemented by mapping through all elements because mini-mongo does not implement the remove operation.
   * So this approach can be used on both client and server side.
   * removeAll should only used for testing purposes, so it doesn't need to be efficient.
   * @returns true
   */
  removeAll() {
    const items = this._collection.find().fetch();
    const instance = this;
    _.forEach(items, (i) => {
      instance.remove(i._id);
    });
    return true;
  }

  /**
   * Default remove function calls remove with the docID.
   * @param docID The docID of the document to be removed.
   */
  remove(docID) {
    this._collection.remove(docID);
  }

  /**
   * Internal helper function to simplify definition of the assertValidRoleForMethod method.
   * @param userId The userID.
   * @param roles An array of roles.
   * @throws { Meteor.Error } If userId is not defined or user is not in the specified roles.
   * @returns True if no error is thrown.
   * @ignore
   */
  _assertRole(userId, roles) {
    if (!userId) {
      throw new Meteor.Error('unauthorized', 'You must be logged in.');
    } else
      if (!Roles.userIsInRole(userId, roles)) {
        throw new Meteor.Error('unauthorized', `You must be one of the following roles: ${roles}`);
      }
    return true;
  }

  /**
   * Default implementation of assertValidRoleForMethod. Asserts that userId is logged in as an Admin.
   * This function should be invoked by all Meteor Methods to assure that the method is invoked by an authorized user.
   * @param userId The userId of the logged in user. Can be null or undefined
   * @throws { Meteor.Error } If there is no logged in user, or the user is not an Admin or Advisor.
   */
  assertValidRoleForMethod(userId) {
    this._assertRole(userId, [ROLE.ADMIN]);
  }

  /**
   * Throws an error if id is not a valid docID in this collection.
   * @param id The docID.
   * @returns The document associated with docID, if docID is defined.
   * @throws { Meteor.Error } If it's not a defined docID.
   */
  assertIsDefined(id) {
    const doc = this.isDefined(id);
    if (!doc) {
      throw new Meteor.Error(`Undefined ID: ${id}`);
    }
    return doc;
  }

  /**
   * The default implementation of checkIntegrity. Returns an array with a string indicating no checker is defined.
   * @param doc The document.
   * @param repair Whether to attempt to repair the collection.
   * @returns {string} An empty array if no problem, otherwise an array of strings indicating all problems found.
   */
  checkIntegrity(doc, repair) { // eslint-disable-line
    return ['No integrity checker defined for this collection'];
  }

}

export default BaseCollection;
