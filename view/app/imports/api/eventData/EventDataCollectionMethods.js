import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { EventData } from './EventDataCollection.js';

export const getRecentEventDataReqIds = new ValidatedMethod({
  name: 'EventData.getRecentEventDataReqIds',
  validate: new SimpleSchema({
    numEvents: {type: Number}
  }).validator({clean: true}),
  run({ numEvents }) {
    if (!this.isSimulation) {
      numEvents = (numEvents > 100) ? 100 : numEvents;

      // Find events that actually have waveform data, which we can determine by checking whether the
      // eventData object has more than the default two fields (_id and request_id).
      // For the future, event data should have an array field that lists all deviceIds that the event included.
      const eventReqIds = EventData.find({}, {sort: {_id: -1}})
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