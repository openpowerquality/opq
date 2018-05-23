import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { defineMethod, removeMethod, updateMethod } from '../base/BaseCollection.methods';
import { UserProfiles } from './UserProfilesCollection';
import { Locations } from '../locations/LocationsCollection';
import { Regions } from '../regions/RegionsCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';
import { withOpqSubscriptions, withLoggedInUser, defineTestFixturesMethod } from '../test/test-utilities';
import { ROLE } from '../opq/Role';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isClient) {
  describe('UserProfilesCollection Meteor Methods ', function test() {
    const collectionName = UserProfiles.getCollectionName();
    const username = 'opqtester@hawaii.edu';
    const firstName = 'Nikola';
    const lastName = 'Tesla';
    const password = 'foo';
    const role = ROLE.ADMIN;

    before(async function () {
      await defineTestFixturesMethod.callPromise(['minimal']);
      await withLoggedInUser();
      await withOpqSubscriptions();
    });

    it('Verify DB fixture', function () {
      // It's useful to verify that the client side has whatever data we expect it to have as shown here.
      // Note that we don't actually need the 'minimal' fixture to test UserProfiles.
      // We're loading it and verifying it just for illustrative purposes.
      expect(Regions.count()).to.equal(2);
      expect(Locations.count()).to.equal(2);
      expect(UserProfiles.count()).to.equal(2);
      expect(OpqBoxes.count()).to.equal(2);
    });

    it('Define Method', async function () {
      const definitionData = { username, firstName, lastName, role, password };
      const docID = await defineMethod.callPromise({ collectionName, definitionData });
      expect(docID).to.exist;
    });

    it('Update Method', async function () {
      const id = UserProfiles.findByUsername(username)._id;
      const newFirstName = 'Nikolai';
      const update = await updateMethod.callPromise({ collectionName, updateData: { id, firstName: newFirstName } });
      expect(update.firstName).to.equal(newFirstName);
    });

    it('Remove Method', async function () {
      const docID = UserProfiles.findByUsername(username)._id;
      const result = await removeMethod.callPromise({ collectionName, docID });
      expect(result).to.be.true;
      expect(() => UserProfiles.findByUsername(username)).to.throw();
    });
  });
}
