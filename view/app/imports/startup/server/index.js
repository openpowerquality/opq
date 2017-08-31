import { Meteor } from 'meteor/meteor';
import './publications.js';
import { startEventSimulation } from '../../api/simulatedEvents/simulatedEventsMethods.js';


const simHandle = startEventSimulation();
Meteor.setTimeout(() => {
  Meteor.clearInterval(simHandle);
  console.log('Event simulation stopped!');
}, 60000 * 60);
