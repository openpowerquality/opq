import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import Moment from 'moment';
import { demapify } from 'es6-mapify';
import { Trends } from './TrendsCollection';

/**
 * Returns an array of daily trend data with the box IDs as their keys
 * @param {String[]} boxIDs: List of box IDs to get data for
 * @param {Number} startDate_ms: Start of range in Unix epoch time
 * @param {Number} endDate_ms: End of range in Unix epoch time
 * @returns An Object of objects, in this form: { boxID: dailyTrends }}.
 */
export const dailyTrends2 = new ValidatedMethod({
  name: 'Trends.dailyTrends2',
  validate: new SimpleSchema({
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startDate_ms: { type: Number },
    endDate_ms: { type: Number },
  }).validator(),
  run({ boxIDs, startDate, endDate }) {
    return boxIDs.map(box_id => Trends.dailyTrendsData(startDate, endDate, box_id));
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
