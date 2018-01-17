import { Meteor } from 'meteor/meteor';
import { Measurements } from '../api/measurements/MeasurementsCollection';
import { Trends } from '../api/trends/TrendsCollection';
import { Events } from '../api/events/EventsCollection';
import { BoxEvents } from '../api/box-events/BoxEventsCollection';
import { OpqBoxes } from '../api/opq-boxes/OpqBoxesCollection';
import { Users } from '../api/users/UsersCollection';
// import { FSFiles, FSChunks } from '../api/eventDataFS/EventDataFSCollection';
import { FSFiles } from '../api/fs-files/FSFilesCollection';
import { FSChunks } from '../api/fs-chunks/FSChunksCollection';

export function getCollection(collectionName) {
  let collection = null;

  switch (collectionName) {
    case 'measurements':
      collection = Measurements;
      break;
    case 'trends':
      collection = Trends;
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
    default:
      throw new Meteor.Error(`Could not find database: ${collectionName}`);
  }

  return collection || null;
}

export function initIntegrityChecks() {
  /* eslint-disable no-console, max-len */
  let messages = 'Integrity check results:';
  let errorCount = 0;
  const resultStatsArr = ['Final Result Statistics\n'];

  const collectionNames = Meteor.settings.public.integrityCheckCollections;
  collectionNames.forEach(colName => {
    const collection = getCollection(colName);
    console.log(`Starting integrity check for collection: ${collection._collectionName} (Document Count: ${collection.count()})`);
    const result = collection.checkIntegrity();
    errorCount += result.length;
    const resultStatistics = `Results for collection: ${collection._collectionName} (Collection Count: ${collection.count()}) (Error Count: ${result.length})`;
    resultStatsArr.push(resultStatistics);
    messages += `\n\n *** ${resultStatistics} ***\n`;
    result.forEach(resultMsg => {
      messages += `\n ${resultMsg}`;
    });

    console.log(`Finished integrity check for collection: ${collection._collectionName} (Error Count: ${result.length})`);
  });

  messages += `\n\n **Integrity check complete! Total error count: ${errorCount}**\n`;

  let resultStats = '';
  resultStatsArr.forEach(stats => {
    resultStats = `${resultStats}\n${stats}\n`;
  });

  return { messages, errorCount, resultStats };
  /* eslint-enable no-console, max-len */
}

export function totalDBDocCount() {
  let docCount = 0;
  const measurementsCount = Measurements.find().count();
  const eventsCount = Events.find().count();
  const boxEventsCount = BoxEvents.find().count();
  const opqBoxesCount = OpqBoxes.find().count();

  docCount = measurementsCount + eventsCount + boxEventsCount + opqBoxesCount;
  return docCount;
}
