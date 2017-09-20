import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { BoxEvents } from './BoxEventCollection.js';
import Moment from 'moment';
import { demapify } from 'es6-mapify';
import { timeUnitString } from "../../utils/utils.js";

export const boxEventsCount = new ValidatedMethod({
  name: 'BoxEvents.BoxEventsCount',
  validate: new SimpleSchema({
    startTime: {type: Date},
    endTime: {type: Date, optional: true}
  }).validator({clean: true}),
  run({ startTime, endTime}) {
    const selector = BoxEvents.queryConstructors().getBoxEvents({ startTime, endTime });
    const boxEvents = BoxEvents.find(selector, {});
    return boxEvents.count();
  }
});

export const boxEventsCountMap = new ValidatedMethod({
  name: 'BoxEvents.BoxEventsCountMap',
  validate: new SimpleSchema({
    timeUnit: {type: String},
    startTime: {type: Date},
    endTime: {type: Date, optional: true}
  }).validator({clean: true}),
  run({ timeUnit, startTime, endTime}) {
    // TimeUnits can be year, month, week, day, dayOfMonth, hourOfDay
    const selector = BoxEvents.queryConstructors().getBoxEvents({ startTime, endTime });
    const boxEvents = BoxEvents.find(selector, {});

    const boxEventsCountMap = new Map();
    boxEvents.forEach(event => {
      const timeUnitKey = timeUnitString(event.eventStart, timeUnit);
      (boxEventsCountMap.has(timeUnitKey)) ? boxEventsCountMap.set(timeUnitKey, boxEventsCountMap.get(timeUnitKey) + 1)
                                           : boxEventsCountMap.set(timeUnitKey, 1);
    });

    return demapify(boxEventsCountMap);
  }
});