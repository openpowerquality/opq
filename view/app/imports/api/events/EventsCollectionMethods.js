import { Mongo } from 'meteor/mongo';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { demapify } from 'es6-mapify';
import { Events } from './EventsCollection.js';
import { timeUnitString } from '../../utils/utils.js';


export const eventMetaDataCount = new ValidatedMethod({
  name: 'EventMetaData.eventMetaDataCount',
  validate: new SimpleSchema({
    startTime: { type: Date },
    endTime: { type: Date, optional: true },
  }).validator({ clean: true }),
  run({ startTime, endTime }) {
    const selector = Events.queryConstructors().getEvents({ startTime, endTime });
    const eventMetaData = Events.find(selector, {});
    return eventMetaData.count();
  },
});

export const eventsCountMap = new ValidatedMethod({
  name: 'EventMetaData.eventsCountMap',
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

export const getEventMetaDataById = new ValidatedMethod({
  name: 'EventMetaData.getEventMetaDataById',
  validate: new SimpleSchema({
    eventMetaDataId: { type: Mongo.ObjectID },
  }).validator({ clean: true }),
  run({ eventMetaDataId }) {
    const eventMetaData = Events.findOne({ _id: eventMetaDataId }, {});
    return eventMetaData;
  },
});

export const getEventByEventID = new ValidatedMethod({
  name: 'EventMetaData.getEventByEventID',
  validate: new SimpleSchema({
    event_id: { type: Number },
  }).validator({ clean: true }),
  run({ event_id }) {
    const eventMetaData = Events.findOne({ event_id }, {});
    return eventMetaData;
  },
});

export const getMostRecentEvent = new ValidatedMethod({
  name: 'EventMetaData.getMostRecentEvent',
  validate: new SimpleSchema({}).validator({ clean: true }),
  run() {
    const mostRecentEvent = Events.findOne({}, { sort: { target_event_start_timestamp_ms: -1 } });
    return mostRecentEvent;
  },
});
