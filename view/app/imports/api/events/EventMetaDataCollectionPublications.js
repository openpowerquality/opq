import { Meteor } from 'meteor/meteor';
import { BoxEvents } from '../box-events/BoxEventsCollection.js';
import { EventMetaData } from './EventsCollection.js'
import { check, Match } from 'meteor/check';

export const eventMetaDataCollectionPublications = () => {
  Meteor.publish(EventMetaData.publicationNames.GET_EVENT_META_DATA, function({startTime, endTime}) {
    check(startTime, Match.Maybe(Number));
    check(endTime, Match.Maybe(Number));

    const selector = EventMetaData.queryConstructors().getEventMetaData({startTime, endTime});
    return EventMetaData.find(selector, {});
  });
};