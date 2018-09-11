import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection';
import { Regions } from '../regions/RegionsCollection';

/**
 * The locations collection provides entities that define locations that can be associated with OPQBoxes, Trends,
 * Events, and other entities in the system.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#locations}
 */
class LocationsCollection extends BaseCollection {

  constructor() {
    super('locations', new SimpleSchema({
      slug: String,
      coordinates: {
        type: Array,
        minCount: 2,
        maxCount: 2
      },
      'coordinates.$': Number,
      description: String,
    }));
    // Guarantee that both slugs and descriptions are unique.
    // if (Meteor.server) {
    //   this._collection.rawCollection().createIndex({ slug: 1 }, { background: true, unique: true });
    //   this._collection.rawCollection().createIndex({ description: 1 }, { background: true, unique: true });
    // }
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
      // TODO: description must also be unique.
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
    return _.isString(slug) && this._collection.findOne({ slug });
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

  /**
   * Returns the location document associated with _id, or throws an error if not found.
   * @param id The location _id
   * @returns {Object} The location document.
   * @throws { Meteor.Error } If the _id is not defined.
   */
  getDocById(id) {
    const docID = new Meteor.Collection.ObjectID(id);
    const doc = this._collection.findOne({ _id: docID }, {});
    if (!doc) {
      throw new Meteor.Error(`Undefined _id ${docID}.`);
    }
    return doc;
  }

  /**
   * Returns an array of all the defined Location documents.
   */
  getDocs() {
    return this._collection.find({}).fetch();
  }

  /**
   * Returns the Location slug associated with description.
   * @param description The location description.
   * @throws { Meteor.Error } If description is not associated with a location.
   * @returns The Location slug.
   */
  findSlugFromDescription(description) {
    const locationDoc = this.findOne({ description });
    if (!locationDoc) {
      throw new Meteor.Error(`Location description ${description} is not defined.`);
    }
    return locationDoc.slug;
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

  /**
   * Returns the Location document associated with _id.
   * @param _id The location _id.
   * @throws { Meteor.Error } If _id is not associated with a location.
   * @returns The Location document.
   */
  findLocationBy_id(_id) {
    const locationDoc = this.findOne({ _id });
    if (!locationDoc) {
      throw new Meteor.Error(`Location _id ${_id} is not defined.`);
    }
    return locationDoc;
  }

  update(docID, args) {
    if (Meteor.isServer) {
      const updateData = {};
      if (args.slug) {
        updateData.slug = args.slug;
      }
      if (args.coordinates) {
        updateData.coordinates = args.coordinates;
      }
      if (args.description) {
        updateData.description = args.description;
      }
      this._collection.update(docID, { $set: updateData });
      return updateData;
    }
    return undefined;
  }

}

/**
 * Provides the singleton instance of this class.
 * @type {LocationsCollection}
 */
export const Locations = new LocationsCollection();
