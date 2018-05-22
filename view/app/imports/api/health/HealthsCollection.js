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
}

/**
 * Provides the singleton instance of this class.
 * @type {HealthsCollection}
 */
export const Healths = new HealthsCollection();
