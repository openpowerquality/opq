import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';


/**
 * The OPQHealth service creates documents representing its findings on the current health of the system.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#health}
 */
class HealthsCollection extends BaseCollection {

  constructor() {
    super('health', new SimpleSchema({
      info: String,
      service: String,
      timestamp: Date,
      status: String,
      serviceID: String,
    }));
  }

  /**
   * Creates the publications for the Health collection. Subscriber must pass in the millisecond value corresponding
   * to the earliest Health document of interest.
   */
  // publish() {
  //   const self = this;
  //   if (Meteor.isServer) {
  //     Meteor.publish(self.getPublicationName(), function ({ startTime }) {
  //       console.log(self.getPublicationName(), startTime);
  //       check(startTime, Date);
  //       // return self.find({ timestamp: { $gt: startTime } }) || self.ready;
  //       return self.find();
  //     });
  //   }
  // }

  /**
   * Default publication of collection (publishes entire collection). Derived classes will often override with
   * their own publish() method, as its generally a bad idea to publish the entire collection to the client.
   */
  publish() {
    if (Meteor.isServer) {
      Meteor.publish(this._collectionName, () => this._collection.find({ timestamp: { $gt: new Date() } }));
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {HealthsCollection}
 */
export const Healths = new HealthsCollection();
