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

  /**
   * Returns a truthy value if the passed slug is a location slug.
   * @param slug A string slug.
   * @returns {*|Object} Truthy if slug is a location slug.
   */
  isLocation(slug) {
    return slug && this._collection.findOne({ slug });
  }

  /**
   * Returns the location document associated with slug, or throws an error if not found.
   * @param slug The location slug
   * @returns {Object} The location document.
   * @throws { Meteor.Error } If the slug is not defined.
   */
  getDoc(slug) {
    const doc = this._collection.findOne({ slug });
    if (!doc) {
      throw new Meteor.Error(`Undefined slug ${slug}.`);
    }
    return doc;
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
