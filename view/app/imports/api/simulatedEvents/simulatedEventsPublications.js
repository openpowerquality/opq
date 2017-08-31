import { Meteor } from 'meteor/meteor';
import SimulatedEvents from './simulatedEvents.js';

Meteor.publish('simulatedEvents', function(startTimeSecondsAgo) {
  const startTimeMs = Date.now() - (startTimeSecondsAgo * 1000);
  const events = SimulatedEvents.find({timestamp_ms: {$gte: startTimeMs}});

  return events;
});