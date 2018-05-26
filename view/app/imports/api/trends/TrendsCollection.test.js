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

    const box_id = '1';
    const calibration_constant = 1;
    const trend1 = { min: -100, max: 100, average: 0 };
    const trend2 = { min: 0, max: 0, average: 0 };
    const trend3 = { min: -50, max: 25, average: 10 };
    const startDateString = '2018-01-01T12:00:00';
    let timestamp_ms = moment(startDateString).valueOf();

    it('#define, #isDefined', function test() {
      // Test that we can create and retrieve a simple Trend document.
      OpqBoxes.define({ box_id, calibration_constant });
      const trendId = Trends.define({ box_id, timestamp_ms, voltage: trend1, frequency: trend1, thd: trend1 });
      expect(Trends.isDefined(trendId)).to.exist;

      // Add two more trends to January 1, 2018 in order to set up further tests.
      timestamp_ms += 1;
      Trends.define({ box_id, timestamp_ms, voltage: trend2, frequency: trend2, thd: trend2 });
      timestamp_ms += 1;
      // No thd field in this last one.
      Trends.define({ box_id, timestamp_ms, voltage: trend3, frequency: trend3 });
    });

    it('#countTrends, #oldestTrend, #newestTrend', function test() {
      expect(Trends.countTrends(box_id)).to.equal(3);
      expect(Trends.oldestTrend(box_id).timestamp_ms).to.equal(timestamp_ms - 2);
      expect(Trends.newestTrend(box_id).timestamp_ms).to.equal(timestamp_ms);
    });

    it('#dailyTrendData (single day)', function test() {
      const dailyTrendData = Trends.dailyTrendData(timestamp_ms, box_id);
      // console.log(dailyTrendData);
      expect(dailyTrendData.frequency.min).to.equal(-100);
      expect(dailyTrendData.frequency.max).to.equal(100);
      expect(Math.trunc(dailyTrendData.frequency.average)).to.equal(3);
      expect(dailyTrendData.thd.average).to.equal(0);
      expect(dailyTrendData.frequency.count).to.equal(3);
      expect(dailyTrendData.thd.count).to.equal(2);
    });

    it('#dailyTrendsData (multiple days)', function test() {
      // Get daily trends for four days. Only day 1 has data.
      const dailyTrendsData = Trends.dailyTrendsData(timestamp_ms, moment(timestamp_ms).add(3, 'day'), box_id);
      // check a few values from jan1 (same as previous test case).
      const jan1key = moment(timestamp_ms).startOf('day').valueOf();
      const jan1TrendData = dailyTrendsData[jan1key];
      expect(jan1TrendData.frequency.min).to.equal(-100);
      expect(jan1TrendData.frequency.max).to.equal(100);
      // check a couple of values from jan2 (note: there is no trend data for this day).
      const jan2key = moment(jan1key).add(1, 'day').startOf('day').valueOf();
      const jan2TrendData = dailyTrendsData[jan2key];
      expect(jan2TrendData.thd.average).to.equal(0);
      expect(jan2TrendData.frequency.count).to.equal(0);
    });
  });
}
