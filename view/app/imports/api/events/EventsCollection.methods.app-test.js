import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { withLoggedInUser, defineTestFixturesMethod, withOpqSubscriptions } from '../test/test-utilities';
import { defineMethod, updateMethod } from '../base/BaseCollection.methods';
import { Events } from './EventsCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isClient) {
  describe('Events Meteor Methods ', function test() {
    const collectionName = Events.getCollectionName();
    const box_id = '2000';
    const name = 'box';
    const description = 'description';
    const calibration_constant = 2.3;
    const unplugged = false;
    const location = 'Test-Location-001';

    before(async function () {
      await defineTestFixturesMethod.callPromise(['minimal']);
      await withLoggedInUser();
      await withOpqSubscriptions();
    });

    it('Define Method', async function () {
      const definitionData = { box_id, name, description, calibration_constant, unplugged, location };
      const docID = await defineMethod.callPromise({ collectionName, definitionData });
      expect(docID).to.exist;
    });

    it('Update Method', async function () {
      const id = Events.findBox(box_id)._id;
      const newUnplugged = true;
      const newLocation = 'Test-Location-002';
      const updateData = { id, unplugged: newUnplugged, location: newLocation };
      const update = await updateMethod.callPromise({ collectionName, updateData });
      expect(update.location).to.equal(newLocation);
    });
  });
}
