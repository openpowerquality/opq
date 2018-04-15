import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { Locations } from '../locations/LocationsCollection';

class RegionsCollection extends BaseCollection {

  /**
   * Creates the Regions collection.
   */
  constructor() {
    super('regions', new SimpleSchema({
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
      if (Locations.findOne({ slug: regionSlug })) {
        throw new Meteor.Error(`Region slug ${regionSlug} is already defined as a location.`);
      }
      if (!Locations.findOne({ slug: locationSlug })) {
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
   * Returns a (potentially empty) array of location slugs associated with the passed region slug.
   * @param regionSlug A slug associated with region. No checking done to see if this is actually a valid region slug.
   * @returns An array of location slugs.
   */
  findLocationsForRegion(regionSlug) {
    const regionDocs = this._collection.find({ regionSlug }).fetch();
    return regionDocs.map(doc => doc.locationSlug);
  }

  /**
   * Returns a (potentially empty) array of region slugs associated with the passed location slug.
   * @param locationSlug A slug associated with location. No checking done to see if this is actually a valid slug.
   * @returns An array of region slugs.
   */
  findRegionsForLocation(locationSlug) {
    const regionDocs = this._collection.find({ locationSlug }).fetch();
    return regionDocs.map(doc => doc.regionSlug);
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
