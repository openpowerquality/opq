import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { Regions } from './RegionsCollection';
import { Locations } from '../locations/LocationsCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isServer) {
  describe('RegionsCollection', function testSuite() {
    const locationSlug1 = 'kailua-abc';
    const locationSlug2 = 'kailua-xyz';
    const coordinates = [1, 2];
    const description1 = 'description abc';
    const description2 = 'description xyz';
    before(function setup() {
      Regions.removeAll();
      Locations.removeAll();
    });

    after(function tearDown() {
      Regions.removeAll();
      Locations.removeAll();
    });

    it('#define, #findLocationsForRegion, #findRegionsForLocation', function test() {
      const regionSlug = 'kailua';
      Locations.define({ slug: locationSlug1, coordinates, description: description1 });
      Locations.define({ slug: locationSlug2, coordinates, description: description2 });
      Regions.define({ regionSlug, locationSlug: locationSlug1 });
      Regions.define({ regionSlug, locationSlug: locationSlug2 });
      expect(Regions.findLocationsForRegion(regionSlug)).to.have.length(2);
      expect(Regions.findRegionsForLocation(locationSlug1)).to.have.length(1);
    });
  });
}
