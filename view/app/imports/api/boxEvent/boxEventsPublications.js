import { Meteor } from 'meteor/meteor';
import BoxEvents from './boxEvents.js';

Meteor.publish('boxEvents', function(startTimeSecondsAgo) {
  const startTimeMs = Date.now() - (startTimeSecondsAgo * 1000);
  const events = BoxEvents.find({eventStart: {$gte: startTimeMs}});

  return events;
});