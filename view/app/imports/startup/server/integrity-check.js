import { Meteor } from 'meteor/meteor';
import { OPQ } from '../../api/opq/Opq';

function checkCollection(name, repair, verbose, maxChecks) {
  console.log(`Checking collection: ${name}, repair: ${repair}, verbose: ${verbose}`);
  const collectionClass = OPQ.getCollection(name);
  let totalChecked = 0;
  let totalProblems = 0;
  collectionClass._collection.find({}, { limit: maxChecks }).forEach(function (doc) {
    const integrityResult = collectionClass.checkIntegrity(doc, repair);
    if ((integrityResult.length > 0) && verbose) {
      console.log(`  ${integrityResult.join()}, DocID: ${JSON.stringify(doc._id)}`);
    }
    totalChecked += 1;
    totalProblems += (integrityResult.length > 0) ? 1 : 0;
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
