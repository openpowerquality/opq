import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import moment from 'moment';
import { withLoggedInUser, defineTestFixturesMethod } from '../test/test-utilities';
import { getEventsInRange } from './EventsCollection.methods';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isClient) {
  describe('Events Meteor Methods ', function test() {

    before(async function () {
      await defineTestFixturesMethod.callPromise(['minimal', 'events']);
      await withLoggedInUser();
    });

    it('getEventsInRange', async function () {
      const boxIDs = ['1000', '1001'];
      const startTime_ms = moment('2018-01-01T09:00:00').valueOf();
      const endTime_ms = moment('2018-01-01T21:00:00').valueOf();
      const events = await getEventsInRange.callPromise({ boxIDs, startTime_ms, endTime_ms });
      expect(events.length).to.equal(2);
      expect(events[0].event_id).to.equal(1);
      expect(events[1].event_id).to.equal(2);
    });
  });
}
