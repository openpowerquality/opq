import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import moment from 'moment';
import { withLoggedInUser, defineTestFixturesMethod } from '../test/test-utilities';
import { dailyTrends } from './TrendsCollection.methods';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isClient) {
  describe('TrendsCollection Meteor Methods ', function test() {

    before(async function () {
      await defineTestFixturesMethod.callPromise(['minimal', 'trends']);
      await withLoggedInUser();
    });

    it('Trends.dailyTrends Method', async function () {
      const boxIDs = ['1000'];
      const startDate_ms = moment('2018-01-01').valueOf();
      const endDate_ms = moment('2018-01-02').valueOf();
      const trendData = await dailyTrends.callPromise({ boxIDs, startDate_ms, endDate_ms });
      const jan1data = trendData['1000'][startDate_ms];
      expect(jan1data).to.exist;
      expect(jan1data.frequency.min).to.equal(60);
      expect(jan1data.frequency.max).to.equal(70);
      expect(jan1data.frequency.average).to.equal(65);
      expect(jan1data.frequency.count).to.equal(2);
    });
  });
}
