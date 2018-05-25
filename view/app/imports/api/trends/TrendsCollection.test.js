import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import moment from 'moment';
import { Trends } from './TrendsCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isServer) {
  describe('TrendsCollection', function testSuite() {
    before(function setup() {
      Trends.removeAll();
      OpqBoxes.removeAll();
    });

    after(function tearDown() {
      Trends.removeAll();
      OpqBoxes.removeAll();
    });

    it('#define, #isDefined, #countTrends, #oldestTrend, #newestTrend', function test() {
      // First test that we can create and retrieve a simple Trend document.
      const box_id = '1';
      const calibration_constant = 1;
      OpqBoxes.define({ box_id, calibration_constant });
      const trend1 = { min: -100, max: 100, average: 0 };
      const trend2 = { min: 0, max: 0, average: 0 };
      const trend3 = { min: -50, max: 25, average: 10 };
      let timestamp_ms = moment().valueOf();
      const trendId = Trends.define({ box_id, timestamp_ms, voltage: trend1, frequency: trend1, thd: trend1 });
      expect(Trends.isDefined(trendId)).to.exist;

      // Now test the oldest, newest, and count class methods.
      timestamp_ms += 1;
      Trends.define({ box_id, timestamp_ms, voltage: trend2, frequency: trend2, thd: trend2 });
      timestamp_ms += 1;
      // No thd field in this last one.
      Trends.define({ box_id, timestamp_ms, voltage: trend3, frequency: trend3 });
      expect(Trends.countTrends(box_id)).to.equal(3);
      expect(Trends.oldestTrend(box_id).timestamp_ms).to.equal(timestamp_ms - 2);
      expect(Trends.newestTrend(box_id).timestamp_ms).to.equal(timestamp_ms);

      // Now test the dailyTrendData computation.
      const dailyTrendData = Trends.dailyTrendData(timestamp_ms, box_id);
      console.log(dailyTrendData);
    });

  });


}
