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
      const trend = { min: -100, max: 100, average: 0 };
      let timestamp_ms = moment().valueOf();
      const trendId = Trends.define({ box_id, timestamp_ms, voltage: trend, frequency: trend, thd: trend });
      expect(Trends.isDefined(trendId)).to.exist;

      // Now test the oldest, newest, and count class methods.
      timestamp_ms += 1;
      Trends.define({ box_id, timestamp_ms, voltage: trend, frequency: trend, thd: trend });
      timestamp_ms += 1;
      Trends.define({ box_id, timestamp_ms, voltage: trend, frequency: trend, thd: trend });
      expect(Trends.countTrends(box_id)).to.equal(3);
      expect(Trends.oldestTrend(box_id).timestamp_ms).to.equal(timestamp_ms - 2);
      expect(Trends.newestTrend(box_id).timestamp_ms).to.equal(timestamp_ms);
    });
  });
}
