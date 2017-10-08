import { Meteor } from 'meteor/meteor';
import { EventData } from '../eventData/EventDataCollection.js';
import { EventMetaData } from './EventMetaDataCollection.js'
import { check, Match } from 'meteor/check';

export const eventMetaDataCollectionPublications = () => {
  Meteor.publish(EventMetaData.publicationNames.GET_EVENT_META_DATA, function({startTime, endTime}) {
    check(startTime, Match.Maybe(Number));
    check(endTime, Match.Maybe(Number));

    const selector = EventMetaData.queryConstructors().getEventMetaData({startTime, endTime});
    return EventMetaData.find(selector, {});
  });
};