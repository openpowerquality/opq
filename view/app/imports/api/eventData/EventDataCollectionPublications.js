import { Meteor } from 'meteor/meteor';
import { EventData } from './EventDataCollection.js';

export const eventDataCollectionPublications = () => {
  Meteor.publish(EventData.publicationNames.EVENT_DATA, function(requestId) {
    check(requestId, Number);
    console.log('sub attempt');
    return EventData.find({request_id: requestId}, {});
  });

  // Meteor.publish(EventData.publicationNames.RECENT_EVENT_DATA, function() {
  //   // Find events that actually have waveform data, which we can currently only check by seeing whether the
  //   // eventData object has more fields than the _id and request_id fields.
  //   // For the future, event data should have an array field that lists all deviceIds that the event included.
  //   const requestIds = EventData.find({}, {sort: {_id: -1}})
  //       .fetch()
  //       .filter(event => Object.keys(event).length > 2)
  //       .map(event => event.request_id.toString()); // Note the toString(). Due to BoxEvents expecting a string on the reqId field. Request fix.
  // })
};