import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { BoxEvents } from './BoxEventsCollection.js';
import { Events } from '../events/EventsCollection';

export const totalBoxEventsCount = new ValidatedMethod({
  name: 'BoxEvents.totalBoxEventsCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return BoxEvents.find({}).count();
  },
});

export const getBoxEvent = new ValidatedMethod({
  name: 'BoxEvents.getBoxEvent',
  validate: new SimpleSchema({
    event_id: { type: Number },
    box_id: { type: String },
  }).validator({ clean: true }),
  run({ event_id, box_id }) {
    if (Meteor.isServer) {
      const boxEvent = BoxEvents.findOne({ event_id, box_id }, {});
      // eslint-disable-next-line max-len, camelcase
      if (!boxEvent) throw new Meteor.Error('BoxEvents document not found', `Document not found for event_number: ${event_id}, box_id: ${box_id}`);
      return boxEvent;
    }
    return null;
  },
});

export const getBoxEventsByType = new ValidatedMethod({
  name: 'BoxEvents.getBoxEventsByType',
  validate: new SimpleSchema({
    itic_region: { type: String },
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startTime_ms: { type: Number },
    endTime_ms: { type: Number },
  }).validator({ clean: true }),
  run({ itic_region, boxIDs, startTime_ms, endTime_ms }) {
    return Events.find({
      itic: { $eq: itic_region },
      boxes_id: { $in: boxIDs },
      event_start_timestamp_ms: { $gte: startTime_ms },
      event_end_timestamp_ms: { $lte: endTime_ms },
    }).fetch();
  },
});
