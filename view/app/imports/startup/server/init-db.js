import { Meteor } from 'meteor/meteor';
import { initIntegrityChecks, getCollection, totalDBDocCount } from '../../modules/integrityChecker';
// import { dumpByEventNumber, eventsBetween } from '../../modules/dbJsonDumper';

function loadDatabase() {
  const dbFilename = Meteor.settings.public.dbRestoreFilename;
  if (dbFilename && (totalDBDocCount() === 0)) {
    const dbJsonFile = JSON.parse(Assets.getText(dbFilename));
    dbJsonFile.forEach(collectionDumpObj => {
      const collectionName = collectionDumpObj.name;
      const collection = getCollection(collectionName);
      if (collection) {
        const collectionContents = collectionDumpObj.contents;
        collection.restoreAll(collectionContents);
      }
    });
  }
}

Meteor.startup(() => {
  loadDatabase();
  const result = initIntegrityChecks();
  console.log(result.messages); // eslint-disable-line no-console
  console.log(result.resultStats); // eslint-disable-line no-console

  // dumpByEventNumber(9356);
  // eventsBetween(1508752800000, 1508839200000);
});

