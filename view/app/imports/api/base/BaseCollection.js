import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';

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
    this._collection = new Mongo.Collection(collectionName, {idGeneration: 'MONGO'});
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
   * @see {@link http://docs.meteor.com/api/collections.html#Mongo-Collection-findOne|Meteor Docs Mongo.Collection.findOne()}
   * @param {Object} selector - A MongoDB selector object.
   * @param {Object} options - A MongoDB options object.
   * @returns {Object} - The document containing the results of the query.
   */
  findOne(selector = {}, options = {}) {
    return this._collection.findOne(selector, options);
  }

  update(selector = {}, modifier = {}, options = {}) {
    return this._collection.update(selector, modifier, options);
  }

  /**
   * Default publication of collection (publishes entire collection). Derived classes should typically just write
   * their own publish() method, as its generally a bad idea to publish the entire collection to the client.
   */
  publish() {
    if (Meteor.isServer) {
      Meteor.publish(this._collectionName, () => this._collection.find());
    }
  }

  /**
   * Subscribes to the publication. Will subscribe on the template instance if it is given.
   * TODO: Implement handling of err/result callback. Look at the Meteor.subscribe implementation for details.
   *
   * @param {String} publicationName - The name of the publication.
   * @param {Object} templateInstance - The template instance.
   * @param {...*} subscriptionArgs - The arguments to pass to the subscription function call.
   * @returns {Object} - The subscription handle object.
   */
  subscribe(publicationName, templateInstance, ...subscriptionArgs) {
    if (Meteor.isClient) {
      const subscribeFn = (templateInstance) ? templateInstance.subscribe.bind(templateInstance) : Meteor.subscribe;
      return subscribeFn(publicationName, ...subscriptionArgs);
    }
  }

  /**
   * Returns an object representing the definition of docID in a format appropriate to the restoreOne function.
   * Must be overridden by each collection.
   * @param docID - A docID from this collection.
   * @returns { Object } - An object representing this document.
   */
  dumpOne(docID) {
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
    const dumpObject = { name: this._collectionName, contents: this.find().map(doc => this.dumpOne(doc._id)) };
    return dumpObject;
  }

  /**
   * Finds and returns the entire document of the given docID.
   * @param {Object} docID - The Mongo.ObjectID of the document to find.
   * @returns {Object} - The found document.
   */
  findDoc(docID) {
    const doc = this.findOne({_id: docID}, {});
    if (!doc) {
      throw new Meteor.Error(`Could not find a document with docID: ${docID} in the collection: ${this._collectionName}.`)
    }
    return doc
  }

  /**
   * Defines the default integrity checker for the base collection. Derived classes are responsible for implementing
   * their own integrity checker, if it is needed.
   * @returns {[String]} - Array containing a string indicating the use of the default integrity checker.
   */
  checkIntegrity() {
    return ['There is no integrity checker defined for this collection.'];
  }
}
export default BaseCollection;