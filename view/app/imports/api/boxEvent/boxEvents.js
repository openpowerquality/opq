import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';

let BoxEvents;
if (Meteor.isServer) {
  //const OpqRemote = new MongoInternals.RemoteCollectionDriver('mongodb://127.0.0.1:9000/opq', {oplogUrl: 'mongodb://127.0.0.1:9000/local'});
  //const OpqRemote = new MongoInternals.RemoteCollectionDriver('mongodb://emilia.ics.hawaii.edu/opq');
  const OpqRemote = new MongoInternals.RemoteCollectionDriver('mongodb://localhost:3002/opq');
  BoxEvents = new Mongo.Collection('boxEvents', {idGeneration: 'MONGO', _driver: OpqRemote });
} else {
  BoxEvents = new Mongo.Collection('boxEvents', {idGeneration: 'MONGO'});
}

export default BoxEvents;
