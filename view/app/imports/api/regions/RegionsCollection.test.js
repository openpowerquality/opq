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
    const description = 'description';
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
      Locations.define({ slug: locationSlug1, coordinates, description });
      Locations.define({ slug: locationSlug2, coordinates, description });
      Regions.define({ regionSlug, locationSlug: locationSlug1 });
      Regions.define({ regionSlug, locationSlug: locationSlug2 });
      expect(Regions.findLocationsForRegion(regionSlug)).to.have.length(2);
      expect(Regions.findRegionsForLocation(locationSlug1)).to.have.length(1);
    });
  });
}
