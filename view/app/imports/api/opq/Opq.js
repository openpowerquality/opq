import { Meteor } from 'meteor/meteor';
import { BoxEvents } from '../box-events/BoxEventsCollection';
import { Events } from '../events/EventsCollection';
import { FSChunks } from '../fs-chunks/FSChunksCollection';
import { FSFiles } from '../fs-files/FSFilesCollection';
import { Healths } from '../health/HealthsCollection';
import { Locations } from '../locations/LocationsCollection';
import { Measurements } from '../measurements/MeasurementsCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { Regions } from '../regions/RegionsCollection';
import { SystemStats } from '../system-stats/SystemStatsCollection';
import { Trends } from '../trends/TrendsCollection';
import { BoxOwners } from '../users/BoxOwnersCollection';
import { UserProfiles } from '../users/UserProfilesCollection';

/**
 * The OPQ class instance provides meta-data about the structure of the OPQ database, including the names and
 * instances of all collections in the system. It is particularly useful for testing.
 * @memberOf api/opq
 */
class OpqClass {

  constructor() {
    // A list of all OPQ API collections in alphabetical order.
    this.collections = [
      BoxEvents,
      Events,
      FSChunks,
      FSFiles,
      Healths,
      Locations,
      Measurements,
      OpqBoxes,
      Regions,
      SystemStats,
      Trends,
      BoxOwners,
      UserProfiles,
    ];

    // A list of OPQ collections in the order they should be loaded from a fixture file.
    this.collectionLoadSequence = [
        Locations,
        Regions,
        OpqBoxes,
        UserProfiles,
        Events,
        BoxEvents,
        Trends,
    ];

    // An object with keys equal to the collection name and values the associated collection instance.
    this.collectionAssociation = {};
    _.forEach(this.collections, collection => {
      this.collectionAssociation[collection._collectionName] = collection;
    });
  }

  /**
   * Return the collection class instance given its name.
   * @param collectionName The name of the collection.
   * @returns The collection class instance.
   * @throws { Meteor.Error } If collectionName does not name a collection.
   */
  getCollection(collectionName) {
    const collection = this.collectionAssociation[collectionName];
    if (!collection) {
      throw new Meteor.Error(`Called OPQ.getCollection with unknown collection name: ${collectionName}`);
    }
    return collection;
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {api/opq.OpqClass}
 * @memberOf api/opq
 */
export const OPQ = new OpqClass();
