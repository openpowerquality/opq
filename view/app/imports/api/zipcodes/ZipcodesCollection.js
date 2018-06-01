import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';

/**
 * Zipcodes collection. Useful for quickly retrieving lat-lng for a given zipcode. Note that zipcodes are indexed.
 * This Zipcodes class collection is barebones and might be entirely unnecessary, since we currently only need
 * the zipcodes collection for single zipcode lookups via Meteor methods.
 */
class ZipcodesCollection extends BaseCollection {

  /**
   * Creates the User Profiles collection.
   */
  constructor() {
    super('zipcodes', new SimpleSchema({
      zipcode: String,
      latitude: Number,
      longitude: Number,
    }));
  }
}

/**
 * Provides the singleton instance of this class.
 */
export const Zipcodes = new ZipcodesCollection();
