import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { UserProfiles } from './UserProfilesCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isServer) {
  describe('UserProfilesCollection', function testSuite() {
    before(function setup() {
      UserProfiles.removeAll();
    });

    after(function tearDown() {
      UserProfiles.removeAll();
    });

    it('#define, #isDefined, #update, #removeIt, #dumpOne, #restoreOne', function test() {
      const username = 'opq@hawaii.edu';
      const firstName = 'John';
      const lastName = 'Smith';
      const role = 'admin';
      const docID = UserProfiles.define({ username, firstName, lastName, role });
      expect(UserProfiles.isDefined(docID)).to.be.true;
      const profile = UserProfiles.findOne({ username });
      expect(profile).to.exist;
      const dumpObject = UserProfiles.dumpOne(docID);
      expect(UserProfiles.remove(dumpObject.username)).to.be.false;
      expect(UserProfiles.isDefined(docID)).to.be.false;
      UserProfiles.restoreOne(dumpObject);
      const id = UserProfiles.findOne({ username })._id;
      expect(UserProfiles.isDefined(id)).to.be.true;
    });
  });
}
