import { Measurements } from '../api/measurements/MeasurementsCollection';
import { Events } from '../api/events/EventsCollection';
import { BoxEvents } from'../api/box-events/BoxEventsCollection';
import { OpqBoxes } from '../api/opq-boxes/OpqBoxesCollection';
import { Users } from '../api/users/UsersCollection';
import { FSFiles, FSChunks } from '../api/eventDataFS/EventDataFSCollection';

export function initIntegrityChecks() {
  let messages = 'Integrity check results:';
  let errorCount = 0;

  const collectionNames = Meteor.settings.public.integrityCheckCollections;
  collectionNames.forEach(colName => {
    const collection = getCollection(colName);
    console.log(`Starting integrity check for collection: ${collection._collectionName} (Document Count: ${collection.count()})`);
    const result = collection.checkIntegrity();
    errorCount += result.length;
    messages += `\n\n *** Results for collection: ${collection._collectionName} (Collection Count: ${collection.count()}) (Error Count: ${result.length}) ***\n`;
    result.forEach(resultMsg => {
      messages += `\n ${resultMsg}`;
    });

    console.log(`Finished integrity check for collection: ${collection._collectionName} (Error Count: ${result.length})`);
  });

  messages += `\n Integrity check complete! Total error count: ${errorCount}`;

  return {messages, errorCount};
}

export function getCollection(collectionName) {
  let collection = null;

  switch (collectionName) {
    case 'measurements':
      collection = Measurements;
      break;
    case 'events':
      collection = Events;
      break;
    case 'box_events':
      collection = BoxEvents;
      break;
    case 'opq_boxes':
      collection = OpqBoxes;
      break;
    case 'users':
      collection = Users;
      break;
    case 'fs.files':
      collection = FSFiles;
      break;
    case 'fs.chunks':
      collection = FSChunks;
      break;
  }

  if (collection) {
    return collection;
  } else {
    throw new Meteor.Error(`Could not find database: ${collectionName}`);
  }
}


export function totalDBDocCount() {
  let docCount = 0;
  const measurementsCount = Measurements.find().count();
  const eventsCount = Events.find().count();
  const boxEventsCount = BoxEvents.find().count();
  const opqBoxesCount = OpqBoxes.find().count();

  docCount = measurementsCount + eventsCount + boxEventsCount + opqBoxesCount;
  return docCount
}