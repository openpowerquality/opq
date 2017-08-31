import { Meteor } from 'meteor/meteor';
import { BoxEvents } from './BoxEventCollection.js';
import { EventData } from '../eventData/EventDataCollection.js';

export const boxEventCollectionPublications = () => {
  Meteor.publish(BoxEvents.publicationNames.RECENT_BOX_EVENTS, function (numRecentEvents) {
    check(numRecentEvents, Number);
    numRecentEvents = (numRecentEvents > 100) ? 100 : numRecentEvents;

    return BoxEvents.find({}, {sort: {eventEnd: -1}, limit: numRecentEvents});
  });

  Meteor.publish(BoxEvents.publicationNames.DAILY_BOX_EVENTS, function() {
    console.log('date: ', Date.now());
    return BoxEvents.find({eventEnd: {$gte: new Date(Date.now() - (24 * 60 * 60 * 1000))}}, {sort: {eventEnd: -1}}); // Potential time zone issue.
  });

  Meteor.publish(BoxEvents.publicationNames.COMPLETE_RECENT_BOX_EVENTS, function (numRecentEvents) {
    check(numRecentEvents, Number);
    numRecentEvents = (numRecentEvents > 100) ? 100 : numRecentEvents;

    // Find events that actually have waveform data, which we can determine by checking whether the
    // eventData object has more than the default two fields (_id and request_id).
    // For the future, event data should have an array field that lists all deviceIds that the event included.
    const requestIds = EventData.find({}, {sort: {_id: -1}})
        .fetch()
        .filter(event => Object.keys(event).length > 2)
        .map(event => event.request_id.toString()); // Note the toString(). Due to BoxEvents expecting a string on the reqId field. Request fix.

    const paginatedRequestIds = requestIds.slice(0, numRecentEvents);

    return BoxEvents.find({reqId: {$in: paginatedRequestIds}}, {});
  });
};