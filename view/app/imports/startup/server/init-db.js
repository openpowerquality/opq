import { checkIntegrity, getCollection, totalDBDocCount } from '../../modules/integrityChecker';

function loadDatabase() {
  const dbFilename = Meteor.settings.public.dbRestoreFilename;
  if (dbFilename && (totalDBDocCount() === 0)) {
    const dbJsonFile = Json.parse(Assets.getText(dbFilename));
    dbJsonFile.forEach(collectionDumpObj => {
      const collectionName = collectionDumpObj.name;
      const collection = getCollection(collectionName);
      if (collection) {
        const collectionContents = collectionDumpObj.contents;
        collection.restoreAll(collectionContents);
      }
    })
  }
}

Meteor.startup(() => {
  loadDatabase();
  const integrityResult = checkIntegrity();
  console.log(result.messages);
});

