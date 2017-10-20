import { Meteor } from 'meteor/meteor';

export const EventDataFSFiles = (Meteor.isServer) ? new Mongo.Collection('fs.files', {idGeneration: 'MONGO', _driver: new MongoInternals.RemoteCollectionDriver('mongodb://localhost:3002/opq')})
                                                  : new Mongo.Collection('fs.files', {idGeneration: 'MONGO'});

export const EventDataFSChunks = (Meteor.isServer) ? new Mongo.Collection('fs.chunks', {idGeneration: 'MONGO', _driver: new MongoInternals.RemoteCollectionDriver('mongodb://localhost:3002/opq')})
                                                   : new Mongo.Collection('fs.chunks', {idGeneration: 'MONGO'});
