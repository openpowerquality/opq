import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

/* eslint-disable indent */

class HealthsCollection extends BaseCollection {

  /**
   * Creates the System Stats collection.
   */
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
   * Not currently checking integrity for this collection.
   * @returns {Array}
   */
  checkIntegrity() { // eslint-disable-line
    const problems = [];
    return problems;
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {HealthsCollection}
 */
export const Healths = new HealthsCollection();
