import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { defineMethod, removeMethod, updateMethod } from '../base/BaseCollection.methods';
import { UserProfiles } from './UserProfilesCollection';
import { withOpqSubscriptions, withLoggedInUser } from '../test/test-utilities';
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
      // defineTestFixturesMethod.call(['minimal'], done);
      await withLoggedInUser();
      await withOpqSubscriptions();
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
