import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Locations } from '../locations/LocationsCollection';

class RegionsCollection extends BaseCollection {

  /**
   * Creates the Regions collection.
   */
  constructor() {
    super('regions', new SimpleSchema({
      _id: Mongo.ObjectID,
      regionSlug: String,
      locationSlug: String,
    }));
  }

  /**
   * Defines a new association between a region and a location.
   * @param {String} regionSlug - A unique string identifying this region. No Location can have this slug.
   * @param {String} locationSlug - A string identifying a previously defined location.
   * @throws { Meteor.Error } If the regionSlug is a location slug, or if the locationSlug is not defined.
   * @returns The newly created document ID.
   */
  define({ regionSlug, locationSlug }) {
    if (Meteor.isServer) {
      if (Locations.findOne({ regionSlug })) {
        throw new Meteor.Error(`Region slug ${regionSlug} is already defined as a location.`);
      }
      if (!Locations.findOne({ locationSlug })) {
        throw new Meteor.Error(`Location slug ${locationSlug} is not defined as a location.`);

      }
      this._collection.upsert(
        { regionSlug, locationSlug },
        { $set: { regionSlug, locationSlug } },
      );
      const docID = this.findOne({ regionSlug, locationSlug })._id;
      return docID;
    }
    return undefined;
  }

  /**
   * Returns an object representing a single Region.
   * @param {Object} docID - The Mongo.ObjectID of the Region.
   * @returns {Object} - An object representing a single Region.
   */
  dumpOne(docID) {
    const doc = this.findDoc(docID);
    const regionSlug = doc.regionSlug;
    const locationSlug = doc.locationSlug;
    return { regionSlug, locationSlug };
  }

  checkIntegrity() {
    const problems = [];
    return problems;
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {RegionsCollection}
 */
export const Regions = new RegionsCollection();
