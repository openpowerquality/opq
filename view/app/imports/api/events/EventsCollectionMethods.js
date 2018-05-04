import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { demapify } from 'es6-mapify';
import { Events } from './EventsCollection.js';
import { timeUnitString } from '../../modules/utils.js';


export const totalEventsCount = new ValidatedMethod({
  name: 'Events.totalEventsCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return Events.find({}).count();
  },
});

export const eventsCountMap = new ValidatedMethod({
  name: 'Events.eventsCountMap',
  validate: new SimpleSchema({
    timeUnit: { type: String },
    startTime: { type: Number },
    endTime: { type: Number, optional: true },
  }).validator({ clean: true }),
  run({ timeUnit, startTime, endTime }) {
    // TimeUnits can be year, month, week, day, dayOfMonth, hourOfDay
    const selector = Events.queryConstructors().getEvents({ startTime, endTime });
    const eventMetaData = Events.find(selector);

    const eventCountMap = new Map();
    eventMetaData.forEach(event => {
      const timeUnitKey = timeUnitString(event.target_event_start_timestamp_ms, timeUnit);
      if (eventCountMap.has(timeUnitKey)) {
        eventCountMap.set(timeUnitKey, eventCountMap.get(timeUnitKey) + 1);
      } else {
        eventCountMap.set(timeUnitKey, 1);
      }
    });

    return demapify(eventCountMap);
  },
});

export const getEventByEventID = new ValidatedMethod({
  name: 'Events.getEventByEventID',
  validate: new SimpleSchema({
    event_id: { type: Number },
  }).validator({ clean: true }),
  run({ event_id }) {
    const eventMetaData = Events.findOne({ event_id }, {});
    return eventMetaData;
  },
});

export const getMostRecentEvent = new ValidatedMethod({
  name: 'Events.getMostRecentEvent',
  validate: new SimpleSchema({
    boxes: { type: Array },
    'boxes.$': { type: String },
  }).validator({ clean: true }),
  run() {
    const mostRecentEvent = Events.findOne({}, { sort: { target_event_start_timestamp_ms: -1 } });
    return mostRecentEvent;
  },
});

/** Returns an array of events that were detected by specified boxes, in a specified range.
 * @param {String[]} boxIDs: List of box IDs to get data for
 * @param {Number} startDate_ms: Start of range in Unix epoch time
 * @param {Number} endDate_ms: End of range in Unix epoch time
 */
export const getEventsInRange = new ValidatedMethod({
  name: 'Events.getEventsInRange',
  validate: new SimpleSchema({
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startTime_ms: { type: Number },
    endTime_ms: { type: Number },
  }).validator({ clean: true }),
  run({ boxIDs, startTime_ms, endTime_ms }) {
    const events = Events.find({
      boxes_triggered: {$in: boxIDs},
      target_event_start_timestamp_ms: {gte: startTime_ms},
    });
    return events;
  },
});
