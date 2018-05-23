import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import Moment from 'moment';
import _ from 'lodash';
import { demapify } from 'es6-mapify';
import { Trends } from './TrendsCollection';

export const totalTrendsCount = new ValidatedMethod({
  name: 'Trends.totalTrendsCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return Trends.find({}).count();
  },
});

export const getMostRecentTrendMonth = new ValidatedMethod({
  name: 'Trends.mostRecentTrendMonth',
  validate: new SimpleSchema({}).validator({ clean: true }),
  run() {
    if (Meteor.isServer) {
      const trend = Trends.findOne({}, { sort: { timestamp_ms: -1 } });
      const trendMoment = Moment(trend.timestamp_ms);
      const month = trendMoment.month(); // 0-indexed month integers (January is 0)
      const year = trendMoment.year();
      return { box_id: trend.box_id, month, year };
    }
    return null;
  },
});


/**
 * Returns daily trend data and range trend data with the box IDs as their keys
 * @param {String[]} boxIDs: List of box IDs to get data for
 * @param {Number} startDate_ms: Start of range in Unix epoch time
 * @param {Number} endDate_ms: End of range in Unix epoch time
 * @returns An array of shape { boxID: { dailyTrends, rangeTrends } }
 *
 * !!! THIS FUNCTION IS FOR REFERENCE, NOT FOR USE !!!
 */
export const dailyTrendsInRange = new ValidatedMethod({
  name: 'Trends.dailyTrendsInRange',
  validate: new SimpleSchema({
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startDate_ms: { type: Number },
    endDate_ms: { type: Number },
  }).validator({ clean: true }),
  run({ boxIDs, startDate_ms, endDate_ms }) {
    // The shape of what our daily and monthly trend summaries will look like.
    const trendSummaryShape = {
      voltage: {
        min: Number.MAX_SAFE_INTEGER,
        minDate: null,
        max: Number.MIN_SAFE_INTEGER,
        maxDate: null,
        average: 0,
        count: 0,
      },
      frequency: {
        min: Number.MAX_SAFE_INTEGER,
        minDate: null,
        max: Number.MIN_SAFE_INTEGER,
        maxDate: null,
        average: 0,
        count: 0,
      },
      thd: {
        min: Number.MAX_SAFE_INTEGER,
        minDate: null,
        max: Number.MIN_SAFE_INTEGER,
        maxDate: null,
        average: 0,
        count: 0,
      },
      totalDocCount: 0,
    };
    // For each box, find the trends associated with it and
    // summarize each day's trends into an object with the
    // timestamp of the start of that day (in ms) as its key
    // i.e. { timestamp: dailyTrendData }
    return Object.assign(...boxIDs.map(boxID => {
      const associatedTrends = Trends.find({
        box_id: boxID,
        timestamp_ms: { $gt: startDate_ms, $lte: Moment(endDate_ms).endOf('day').valueOf() },
      }).fetch();

      // New Moments are instantiated every time, because they mutate even when reassigned to a variable.
      const start = Moment(startDate_ms);
      const end = Moment(endDate_ms);
      // Create structure of the dailyTrend object
      const dailyTrends = new Map();
      for (let i = start.startOf('day'); i <= end.startOf('day'); i = i.add(1, 'days')) {
        dailyTrends.set(i.valueOf(), _.cloneDeep(trendSummaryShape));
      }

      // Input real values into the dailyTrend object
      associatedTrends.forEach(trend => {
        const trendDay_ms = Moment(trend.timestamp_ms).startOf('day').valueOf();
        const dtv = dailyTrends.get(trendDay_ms); // Daily Trend Values
        dtv.totalDocCount++;

        // Voltage
        if (trend.voltage) {
          dtv.voltage.count++;
          if (trend.voltage.min < dtv.voltage.min) {
            dtv.voltage.min = trend.voltage.min;
            dtv.voltage.minDate = trend.timestamp_ms;
          }
          if (trend.voltage.max > dtv.voltage.max) {
            dtv.voltage.max = trend.voltage.max;
            dtv.voltage.maxDate = trend.timestamp_ms;
          }
          dtv.voltage.average += (trend.voltage.average - dtv.voltage.average) / dtv.voltage.count;
        }
        // Frequency
        if (trend.frequency) {
          dtv.frequency.count++;
          if (trend.frequency.min < dtv.frequency.min) {
            dtv.frequency.min = trend.frequency.min;
            dtv.frequency.minDate = trend.timestamp_ms;
          }
          if (trend.frequency.max > dtv.frequency.max) {
            dtv.frequency.max = trend.frequency.max;
            dtv.frequency.maxDate = trend.timestamp_ms;
          }
          dtv.frequency.average += (trend.frequency.average - dtv.frequency.average) / dtv.frequency.count;
        }
        // THD
        if (trend.thd) {
          dtv.thd.count++;
          if (trend.thd.min < dtv.thd.min) {
            dtv.thd.min = trend.thd.min;
            dtv.thd.minDate = trend.timestamp_ms;
          }
          if (trend.thd.max > dtv.thd.max) {
            dtv.thd.max = trend.thd.max;
            dtv.thd.maxDate = trend.timestamp_ms;
          }
          dtv.thd.average += (trend.thd.average - dtv.thd.average) / dtv.thd.count;
        }
      });

      // Delete fields that are empty
      dailyTrends.forEach(dtv => {
        if (dtv.voltage.count === 0) delete dtv.voltage; // eslint-disable-line no-param-reassign
        if (dtv.frequency.count === 0) delete dtv.frequency; // eslint-disable-line no-param-reassign
        if (dtv.thd.count === 0) delete dtv.thd; // eslint-disable-line no-param-reassign
      });
      // Daily uptime calculations
      dailyTrends.forEach(dtv => {
        // This number is not accurate, but will be used until a better method is found.
        dtv.uptime = (dtv.totalDocCount / 1440) * 100; // eslint-disable-line no-param-reassign
      });

      // Calculates summary for the entire range.
      const rtv = _.cloneDeep(trendSummaryShape); // rtv = range trend value
      dailyTrends.forEach(dtv => { // dtv = Daily Trend Values
        // Represents the true total doc count of all trend documents parsed for this range.
        rtv.totalDocCount += dtv.totalDocCount;

        // Voltage
        if (dtv.voltage) {
          rtv.voltage.count++;
          if (dtv.voltage.min < rtv.voltage.min) {
            rtv.voltage.min = dtv.voltage.min;
            rtv.voltage.minDate = dtv.voltage.minDate;
          }
          if (dtv.voltage.max > rtv.voltage.max) {
            rtv.voltage.max = dtv.voltage.max;
            rtv.voltage.maxDate = dtv.voltage.maxDate;
          }
          rtv.voltage.average += (dtv.voltage.average - rtv.voltage.average) / rtv.voltage.count;
        }
        // Frequency
        if (dtv.frequency) {
          rtv.frequency.count++;
          if (dtv.frequency.min < rtv.frequency.min) {
            rtv.frequency.min = dtv.frequency.min;
            rtv.frequency.minDate = dtv.frequency.minDate;
          }
          if (dtv.frequency.max > rtv.frequency.max) {
            rtv.frequency.max = dtv.frequency.max;
            rtv.frequency.maxDate = dtv.frequency.maxDate;
          }
          rtv.frequency.average += (dtv.frequency.average - rtv.frequency.average) / rtv.frequency.count;
        }
        // THD
        if (dtv.thd) {
          rtv.thd.count++;
          if (dtv.thd.min < rtv.thd.min) {
            rtv.thd.min = dtv.thd.min;
            rtv.thd.minDate = dtv.thd.minDate;
          }
          if (dtv.thd.max > rtv.thd.max) {
            rtv.thd.max = dtv.thd.max;
            rtv.thd.maxDate = dtv.thd.maxDate;
          }
          rtv.thd.average += (dtv.thd.average - rtv.thd.average) / rtv.thd.count;
        }
      });

      // Delete empty fields
      if (rtv.voltage.count === 0) delete rtv.voltage; // eslint-disable-line no-param-reassign
      if (rtv.frequency.count === 0) delete rtv.frequency; // eslint-disable-line no-param-reassign
      if (rtv.thd.count === 0) delete rtv.thd; // eslint-disable-line no-param-reassign

      return { [boxID]: { dailyTrends: demapify(dailyTrends), rangeTrends: rtv } };
    }));
  },
});

/**
 * Returns an array of daily trend data with the box IDs as their keys
 * @param {String[]} boxIDs: List of box IDs to get data for
 * @param {Number} startDate_ms: Start of range in Unix epoch time
 * @param {Number} endDate_ms: End of range in Unix epoch time
 * @returns An Object of objects, in this form: { boxID: dailyTrends }}.
 */
export const dailyTrends = new ValidatedMethod({
  name: 'Trends.dailyTrends',
  validate: new SimpleSchema({
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startDate_ms: { type: Number },
    endDate_ms: { type: Number },
  }).validator({ clean: true }),
  run({ boxIDs, startDate_ms, endDate_ms }) {
    // For each box, find the trends associated with it and
    // summarize each day's trends into an object with the
    // timestamp of the start of that day (in ms) as its key
    // i.e. { timestamp: dailyTrendData }
    return Object.assign(...boxIDs.map(boxID => {
      const associatedTrends = Trends.find({
        box_id: boxID,
        timestamp_ms: { $gt: startDate_ms, $lte: Moment(endDate_ms).endOf('day').valueOf() },
      }).fetch();

      // New Moments are instantiated every time, because they are mutable.
      const start = Moment(startDate_ms);
      const end = Moment(endDate_ms);
      // Create structure of the dailyTrend object
      const dailyTrendsMap = new Map();
      for (let i = start.startOf('day'); i <= end.startOf('day'); i = i.add(1, 'days')) {
        dailyTrendsMap.set(i.valueOf(), {
          voltage: {
            min: Infinity,
            max: -Infinity,
            average: 0,
            count: 0,
          },
          frequency: {
            min: Infinity,
            max: -Infinity,
            average: 0,
            count: 0,
          },
          thd: {
            min: Infinity,
            max: -Infinity,
            average: 0,
            count: 0,
          },
        });
      }

      // Input real values into the dailyTrend object
      associatedTrends.forEach(trend => {
        const trendDay_ms = Moment(trend.timestamp_ms).startOf('day').valueOf();
        const dtv = dailyTrendsMap.get(trendDay_ms); // Daily Trend Values

        // Voltage
        if (trend.voltage) {
          dtv.voltage.count++;
          if (trend.voltage.min < dtv.voltage.min) dtv.voltage.min = trend.voltage.min;
          if (trend.voltage.max > dtv.voltage.max) dtv.voltage.max = trend.voltage.max;
          dtv.voltage.average += (trend.voltage.average - dtv.voltage.average) / dtv.voltage.count;
        }
        // Frequency
        if (trend.frequency) {
          dtv.frequency.count++;
          if (trend.frequency.min < dtv.frequency.min) dtv.frequency.min = trend.frequency.min;
          if (trend.frequency.max > dtv.frequency.max) dtv.frequency.max = trend.frequency.max;
          dtv.frequency.average += (trend.frequency.average - dtv.frequency.average) / dtv.frequency.count;
        }
        // THD
        if (trend.thd) {
          dtv.thd.count++;
          if (trend.thd.min < dtv.thd.min) dtv.thd.min = trend.thd.min;
          if (trend.thd.max > dtv.thd.max) dtv.thd.max = trend.thd.max;
          dtv.thd.average += (trend.thd.average - dtv.thd.average) / dtv.thd.count;
        }
      });

      // Delete fields that are empty
      dailyTrendsMap.forEach(dtv => {
        if (dtv.voltage.count === 0) delete dtv.voltage; // eslint-disable-line no-param-reassign
        else delete dtv.voltage.count; // eslint-disable-line no-param-reassign
        if (dtv.frequency.count === 0) delete dtv.frequency; // eslint-disable-line no-param-reassign
        else delete dtv.frequency.count; // eslint-disable-line no-param-reassign
        if (dtv.thd.count === 0) delete dtv.thd; // eslint-disable-line no-param-reassign
        else delete dtv.thd.count; // eslint-disable-line no-param-reassign
      });

      return { [boxID]: demapify(dailyTrendsMap) };
    }));
  },
});
