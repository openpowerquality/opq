import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { BoxEvents } from './BoxEventsCollection.js';

export const getRecentEventDataReqIds = new ValidatedMethod({
  name: 'BoxEvents.getRecentEventDataReqIds',
  validate: new SimpleSchema({
    numEvents: {type: Number}
  }).validator({clean: true}),
  run({ numEvents }) {
    if (!this.isSimulation) {
      numEvents = (numEvents > 100) ? 100 : numEvents;

      // Find events that actually have waveform data, which we can determine by checking whether the
      // eventData object has more than the default two fields (_id and request_id).
      // For the future, event data should have an array field that lists all deviceIds that the event included.
      const eventReqIds = BoxEvents.find({}, {sort: {_id: -1}})
          .fetch()
          .filter(event => Object.keys(event).length > 2)
          .map(event => {
            return {
              _id: event._id,
              request_id: event.request_id
            }
          });

      return eventReqIds.slice(0, numEvents);
    }
  }
});

export const getEventData = new ValidatedMethod({
  name: 'BoxEvents.getEventData',
  validate: new SimpleSchema({
    event_number: {type: Number},
    box_id: {type: Number}
  }).validator({clean: true}),
  run({ event_number, box_id}) {
    if (!this.isSimulation) {
      const eventData = BoxEvents.findOne({event_number, box_id}, {});
      if (!eventData) throw new Meteor.Error('BoxEvents document not found', `Document not found for event_number: ${event_number}, box_id: ${box_id}`);
      return eventData;
    }
  }
});