import { Meteor } from 'meteor/meteor';
import moment from 'moment';
import { SyncedCron } from 'meteor/littledata:synced-cron';
import { OPQ } from '../../api/opq/Opq';

/**
 * Checks a collection, printing to console when checking starts and completes, as well as the strings returned
 * from the collection-specific integrityCheck() function to provide details on what problems were encountered and
 * how they were resolved.
 * @param name The name of the Mongo collection to check.
 * @param repair True if the collection-specific repair() method should be called on documents that fail the check.
 * @param verbose True if strings should be printed out detailing each document that failed the check.
 * @param maxChecks The maximum number of documents in the collection to check.
 */
function checkCollection(name, repair, verbose, maxChecks) {
  // We want to check the most recently added documents first, and specify the number of documents to check based on
  // the collection. The following variable accomplishes that.
  const findOptions = {
    events: { limit: maxChecks[name], sort: { event_id: -1 } },
    box_events: { limit: maxChecks[name], sort: { event_id: 1 } },
    opq_boxes: { limit: maxChecks[name], sort: { box_id: 1 } },
  };
  const collectionClass = OPQ.getCollection(name);
  console.log(`  Checking ${name} (${collectionClass.count()} docs) repair: ${repair}, verbose: ${verbose}, maxChecks: ${maxChecks[name]}`); // eslint-disable-line
  let totalChecked = 0;
  let totalProblems = 0;
  collectionClass._collection.find({}, findOptions[name]).forEach(function (doc) {
    const integrityResult = collectionClass.checkIntegrity(doc, repair);
    if ((integrityResult.problems.length > 0) && verbose) {
      console.log(`  ${integrityResult.docName}:`);
      console.log(`    Problems: ${integrityResult.problems.join()}`);
      if (integrityResult.repair) {
        console.log(`    Repair: ${integrityResult.repair}`);
      }
    }
    totalChecked += 1;
    totalProblems += (integrityResult.problems.length > 0) ? 1 : 0;
    if ((totalChecked % 10000) === 0) {
      console.log(`  Completed checking ${totalChecked} ${name} docs, ${totalProblems} problems so far.`);
    }
  });
  console.log(`  Finished collection: ${name}: total: ${totalChecked}, problems: ${totalProblems}`);
}

/**
 * Sets up a cron job to run integrity checking once a day at 1:00am.
 */
function startupIntegrityCheck() {
  // If not in test mode and if integrity checking is enabled.
  const testMode = Meteor.isTest || Meteor.isAppTest;
  const enabled = Meteor.settings.integrityCheck && Meteor.settings.integrityCheck.enabled;
  if (!testMode && enabled) {
    const parseText = 'at 1:00 am';
    SyncedCron.add({
      name: 'Run Integrity Checking',
      schedule(parser) {
        return parser.text(parseText); // Parser is a later.js parse object.
      },
      job() {
        console.log(`Integrity Check: started at ${moment().format('lll')}`);
        const repair = Meteor.settings.integrityCheck.repair;
        const verbose = Meteor.settings.integrityCheck.verbose;
        const maxChecks = Meteor.settings.integrityCheck.maxChecks;
        Meteor.settings.integrityCheck.collections.forEach(name => checkCollection(name, repair, verbose, maxChecks));
        console.log(`Integrity check: finished at ${moment().format('lll')}`);
      },
    });
    console.log(`Starting SyncedCron to run integrity check ${parseText}`);
    SyncedCron.start();
  }
}

Meteor.startup(() => {
  startupIntegrityCheck();
});
