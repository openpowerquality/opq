import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import _ from 'lodash';
import Moment from 'moment';
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
    const startToday = Moment().startOf('day').valueOf();
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
   * @param { String | Object } name The docID, or an object specifying a document.
   * @returns {boolean} True if name exists in this collection.
   */
  isDefined(name) {
    return (
      !!this._collection.findOne(name) ||
      !!this._collection.findOne({ name }) ||
      !!this._collection.findOne({ _id: name }));
  }

  /**
   * Update the collection.
   * @param selector
   * @param modifier
   * @param options
   * @returns {any}
   */
  update(selector = {}, modifier = {}, options = {}) {
    return this._collection.update(selector, modifier, options);
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
   * Returns an object representing the definition of docID in a format appropriate to the restoreOne function.
   * Must be overridden by each collection.
   * @param docID - A docID from this collection.
   * @returns { Object } - An object representing this document.
   */
  dumpOne(docID) { // eslint-disable-line no-unused-vars
    throw new Meteor.Error(`Default dumpOne method invoked by collection ${this._collectionName}`);
  }

  /**
   * Dumps the entire collection as a single object with two fields: name and contents.
   * The name is the name of the collection.
   * The contents is an array of all documents within the collection. These documents are generated using the
   * dumpOne() method and subsequently are meant to be used with the restore() method.
   * @returns {Object} An object representing the contents of this collection.
   */
  dumpAll() {
    return { name: this._collectionName, contents: this.find().map(doc => this.dumpOne(doc._id)) };
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
   * Defines the default integrity checker for the base collection. Derived classes are responsible for implementing
   * their own integrity checker, if it is needed.
   * @returns {[String]} - Array containing a string indicating the use of the default integrity checker.
   */
  checkIntegrity() { // eslint-disable-line class-methods-use-this
    return ['There is no integrity checker defined for this collection.'];
  }

  /**
   * Defines a single collection document represented by dumpObject.
   * @returns {String} - The newly created document ID.
   */
  restoreOne(dumpObject) {
    if (typeof this.define === 'function') {
      return this.define(dumpObject);
    }
    return null;
  }

  /**
   * Defines each collection entity given by the passed array of dumpObjects.
   * @param dumpObjects - The array of objects representing entities of the collection.
   */
  restoreAll(dumpObjects) {
    _.each(dumpObjects, dumpObject => this.restoreOne(dumpObject));
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

}

export default BaseCollection;
