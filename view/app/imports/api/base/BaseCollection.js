import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';

/**
 * BaseCollection is an abstract superclass of all other collection classes.
 */
class BaseCollection {

  /**
   * Superclass constructor for all collections.
   * Defines internal fields required by all collections.
   * @param {String} type - The name of the collection, defined by the subclass.
   * @param {SimpleSchema} schema - The schema to validate collection fields.
   */
  constructor(type, collectionName = null, schema, remoteAddress = null) {
    this._createdAt = new Date();
    console.log('Class created at: ', this._createdAt);
    this._type = type;
    this._collectionName = (collectionName) ? collectionName : `${type}Collection`;
    this._schema = schema;

    this._collection = (remoteAddress && Meteor.isServer) ?
        new Mongo.Collection(this._collectionName, {
          idGeneration: 'MONGO', _driver: new MongoInternals.RemoteCollectionDriver(remoteAddress)
        })
        :
        new Mongo.Collection(this._collectionName, {idGeneration: 'MONGO'});

    this._collection.attachSchema(this._schema);
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
  find(selector, options) {
    const theSelector = (typeof selector === 'undefined') ? {} : selector;
    return this._collection.find(theSelector, options);
  }

  /**
   * Calls the MongoDB native findOne() on this collection.
   * @see {@link http://docs.meteor.com/api/collections.html#Mongo-Collection-findOne|Meteor Docs Mongo.Collection.findOne()}
   * @param {Object} selector - A MongoDB selector object.
   * @param {Object} options - A MongoDB options object.
   * @returns {Object} - The document containing the results of the query.
   */
  findOne(selector, options) {
    const theSelector = (typeof selector === 'undefined') ? {} : selector;
    return this._collection.findOne(theSelector, options);
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
}

export default BaseCollection;