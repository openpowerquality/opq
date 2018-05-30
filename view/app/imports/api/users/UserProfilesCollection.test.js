import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { UserProfiles } from './UserProfilesCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { ROLE } from '../opq/Role';

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

    it('#define, #isDefined, #findBoxIds, #findDoc, #findOne, #remove', function test() {
      const username = 'opq@hawaii.edu';
      const firstName = 'John';
      const lastName = 'Smith';
      const password = 'foo';
      const boxId = '1';
      OpqBoxes.define({ box_id: boxId, name: 'Test Box 1' });
      const boxIds = [boxId];
      let role = ROLE.ADMIN;
      const profileID = UserProfiles.define({ username, password, firstName, lastName, role, boxIds });
      expect(UserProfiles.isDefined(profileID)).to.exist;
      // Check that we can update the username by calling define again.
      role = 'user';
      const profileID2 = UserProfiles.define({ username, password, firstName, lastName, role });
      expect(profileID).to.deep.equal(profileID2);
      // Check that we've overwritten the previous values for boxIds and role.
      expect(UserProfiles.findDoc(profileID2).role).to.equal('user');
      const profile = UserProfiles.findOne({ username });
      expect(profile).to.exist;
      expect(profile.role).to.equal(role);
    });
  });
}
