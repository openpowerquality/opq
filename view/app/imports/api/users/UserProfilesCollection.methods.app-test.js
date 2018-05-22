import { Meteor } from 'meteor/meteor';
import { defineMethod, removeItMethod, updateMethod } from '../base/BaseCollection.methods';
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

    // before(function (done) {
    //   defineTestFixturesMethod.call(['minimal'], done);
    // });

    it('Define Method', async function () {
      await withLoggedInUser();
      await withOpqSubscriptions();
      const definitionData = { username, firstName, lastName, role, password };
      await defineMethod.callPromise({ collectionName, definitionData });
    });

    it('Update Method', async function () {
      const id = UserProfiles.findByUsername(username)._id;
      await updateMethod.callPromise({ collectionName, updateData: { id, firstName: 'Nikolai' } });
    });

    it('Remove Method', async function () {
      const id = UserProfiles.findByUsername(username)._id;
      await removeItMethod.callPromise({ collectionName, id });
    });
  });
}
