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

    it('#define, #isDefined, #findBoxIds, #findDoc, #findOne, #remove, #dumpOne, #restoreOne', function test() {
      const username = 'opq@hawaii.edu';
      const firstName = 'John';
      const lastName = 'Smith';
      const password = 'foo';
      const boxIds = ['1', '2'];
      let role = 'admin';
      const profileID = UserProfiles.define({ username, password, firstName, lastName, role, boxIds });
      expect(UserProfiles.isDefined(profileID)).to.be.true;
      // Check that we can update the username by calling define again.
      role = 'user';
      const profileID2 = UserProfiles.define({ username, password, firstName, lastName, role });
      expect(profileID).to.deep.equal(profileID2);
      // Check that we've overwritten the previous values for boxIds and role.
      expect(UserProfiles.findDoc(profileID2).role).to.equal('user');
      const profile = UserProfiles.findOne({ username });
      expect(profile).to.exist;
      expect(profile.role).to.equal(role);

      // Check dump and restore.
      const dumpObject = UserProfiles.dumpOne(profileID);
      expect(UserProfiles.remove(dumpObject.username)).to.be.true;
      expect(UserProfiles.isDefined(profileID)).to.be.false;
      UserProfiles.restoreOne(_.extend(dumpObject, { password }));
      const id = UserProfiles.findOne({ username })._id;
      expect(UserProfiles.isDefined(id)).to.be.true;
    });
  });
}
