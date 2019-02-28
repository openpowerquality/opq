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
   * Creates the publications for the Health collection. Subscriber must pass in a Date corresponding
   * to the earliest Health document of interest.
   */
  publish() {
    const self = this;
    if (Meteor.isServer) {
      Meteor.publish(this._collectionName, function ({ startTime = new Date() } = {}) {
        check(startTime, Date);
        return self._collection.find({ timestamp: { $gt: startTime } });
      });
    }
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {HealthsCollection}
 */
export const Healths = new HealthsCollection();
