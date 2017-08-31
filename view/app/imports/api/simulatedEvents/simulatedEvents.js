import { Mongo } from 'meteor/mongo';

const SimulatedEvents = new Mongo.Collection('simulatedEvents', {idGeneration: 'MONGO'});

export default SimulatedEvents;

