import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { BoxEvents } from './BoxEventsCollection.js';

export const getRecentEventDataReqIds = new ValidatedMethod({
  name: 'BoxEvents.getRecentEventDataReqIds',
  validate: new SimpleSchema({
    numEvents: { type: Number },
  }).validator({ clean: true }),
  run({ numEvents }) {
    if (!this.isSimulation) {
      const numberOfEvents = (numEvents > 100) ? 100 : numEvents;

      // Find events that actually have waveform data, which we can determine by checking whether the
      // eventData object has more than the default two fields (_id and request_id).
      // For the future, event data should have an array field that lists all deviceIds that the event included.
      const eventReqIds = BoxEvents.find({}, { sort: { _id: -1 } })
          .fetch()
          .filter(event => Object.keys(event).length > 2)
          .map(event => ({
            _id: event._id,
            request_id: event.request_id,
          }));

      return eventReqIds.slice(0, numberOfEvents);
    }
    return null;
  },
});

export const getBoxEvent = new ValidatedMethod({
  name: 'BoxEvents.getBoxEvent',
  validate: new SimpleSchema({
    event_id: { type: Number },
    box_id: { type: String },
  }).validator({ clean: true }),
  run({ event_id, box_id }) {
    if (!this.isSimulation) {
      const boxEvent = BoxEvents.findOne({ event_id, box_id }, {});
      // eslint-disable-next-line max-len, camelcase
      if (!boxEvent) throw new Meteor.Error('BoxEvents document not found', `Document not found for event_number: ${event_id}, box_id: ${box_id}`);
      return boxEvent;
    }
    return null;
  },
});
