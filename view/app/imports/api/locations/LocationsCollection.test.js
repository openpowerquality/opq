import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { Locations } from './LocationsCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isServer) {
  describe('LocationsCollection', function testSuite() {
    before(function setup() {
      Locations.removeAll();
    });

    after(function tearDown() {
      Locations.removeAll();
    });

    it('#define, #findLocation', function test() {
      const slug = 'kailua-pmj';
      const coordinates = [1, 2];
      const description = 'Home in Kailua, HI';
      Locations.define({ slug, coordinates, description });
      expect(Locations.findLocation(slug)).to.exist;
      Locations.define({ slug, coordinates, description: 'changed' });
      const locationDoc = Locations.findLocation(slug);
      expect(locationDoc.description).to.equal('changed');
    });
  });
}
