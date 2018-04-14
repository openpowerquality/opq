import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';
import { Regions } from '../regions/RegionsCollection';

class LocationsCollection extends BaseCollection {

  /**
   * Creates the Locations collection.
   */
  constructor() {
    super('locations', new SimpleSchema({
      slug: String,
      coordinates: Array,
      'coordinates.$': Number,
      description: String,
    }));
  }

  /**
   * Defines a new Locations document.
   * @param {String} slug - A unique string identifying this location. If it exists, it will be overwritten.
   * @param {Array} coordinates - An array of two numbers: longitude followed by latitude.
   * @param {String} description - Further information about the location.
   * @returns The newly created document ID.
   */
  define({ slug, coordinates, description }) {
    if (Meteor.isServer) {

      if (this.findOne({ slug })) {
        console.log(`Slug ${slug} is being redefined.`);
      }
      if (Regions.findOne({ regionSlug: slug })) {
        throw new Meteor.Error(`Slug ${slug} is already defined as a region.`);
      }
      this._collection.upsert(
        { slug },
        { $set: { slug, coordinates, description } },
      );
      const docID = this.findOne({ slug })._id;
      return docID;
    }
    return undefined;
  }

  checkIntegrity() {
    const problems = [];
    return problems;
  }

  /**
   * Returns the Location document associated with slug.
   * @param slug The location slug.
   * @throws { Meteor.Error } If slug is not associated with a location.
   * @returns The Location document.
   */
  findLocation(slug) {
    const locationDoc = this.findOne({ slug });
    if (!locationDoc) {
      throw new Meteor.Error(`Location slug ${slug} is not defined.`);
    }
    return locationDoc;
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {LocationsCollection}
 */
export const Locations = new LocationsCollection();
