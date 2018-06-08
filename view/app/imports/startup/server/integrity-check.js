import { Meteor } from 'meteor/meteor';
import { OPQ } from '../../api/opq/Opq';


function checkCollection(name, repair, verbose, maxChecks) {
  // We want to check the most recently added documents first, and specify the number of documents to check based on
  // the collection. The following variable accomplishes that.
  const findOptions = {
    events: { limit: maxChecks[name], sort: { event_id: -1 } },
    box_events: { limit: maxChecks[name], sort: { event_id: 1 } },
  };
  const collectionClass = OPQ.getCollection(name);
  console.log(`Checking ${name} (${collectionClass.count()} docs) repair: ${repair}, verbose: ${verbose}, maxChecks: ${maxChecks[name]}`); // eslint-disable-line
  let totalChecked = 0;
  let totalProblems = 0;
  collectionClass._collection.find({}, findOptions[name]).forEach(function (doc) {
    const integrityResult = collectionClass.checkIntegrity(doc, repair);
    if ((integrityResult.problems.length > 0) && verbose) {
      console.log(`${integrityResult.docName}:`);
      console.log(`  Problems: ${integrityResult.problems.join()}`);
      if (integrityResult.repair) {
        console.log(`  Repair: ${integrityResult.repair}`);
      }
    }
    totalChecked += 1;
    totalProblems += (integrityResult.problems.length > 0) ? 1 : 0;
    if ((totalChecked % 10000) === 0) {
      console.log(`Completed checking ${totalChecked} ${name} docs, ${totalProblems} problems so far.`);
    }
  });
  console.log(`Finished collection: ${name}: total: ${totalChecked}, problems: ${totalProblems}`);
}

function startupIntegrityCheck() {
  if (Meteor.settings.integrityCheck.enabled) {
    console.log('Starting Integrity Check.');
    const repair = Meteor.settings.integrityCheck.repair;
    const verbose = Meteor.settings.integrityCheck.verbose;
    const maxChecks = Meteor.settings.integrityCheck.maxChecks;
    Meteor.settings.integrityCheck.collections.forEach(name => checkCollection(name, repair, verbose, maxChecks));
  }
}

Meteor.startup(() => {
  startupIntegrityCheck();
});
