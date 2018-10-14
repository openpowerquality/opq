import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { BoxEvents } from './BoxEventsCollection.js';

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
      if (!boxEvent) {
        throw new Meteor.Error(`BoxEvents document not found for event_number: ${event_id}, box_id: ${box_id}`);
      }
      return boxEvent;
    }
    return null;
  },
});

export const getBoxEvents = new ValidatedMethod({
  name: 'BoxEvents.getBoxEvents',
  validate: new SimpleSchema({
    event_id: { type: Number },
    box_ids: { type: Array },
    'box_ids.$': { type: String },
  }).validator({ clean: true }),
  run({ event_id, box_ids }) {
    if (Meteor.isServer) {
      const boxEvents = BoxEvents.find({ event_id, box_id: { $in: box_ids } }).fetch();
      if (!boxEvents.length) {
        const boxIdMessage = (box_ids.length) ? `box_ids: ${box_ids}` : 'box_ids: None';
        throw new Meteor.Error(
            'no-box-events-found',
            `No BoxEvent documents found for event_id: ${event_id}, ${boxIdMessage}`,
        );
      }
      return boxEvents;
    }
    return null;
  },
});
