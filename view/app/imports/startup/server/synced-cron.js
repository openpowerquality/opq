import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

SyncedCron.config({
  log: Meteor.settings.syncedCron && Meteor.settings.syncedCron.logging,
});

function startupSystemStatsCronjob() {
  // Only set up Cron Job when not in Test mode.
  if (!Meteor.isTest && !Meteor.isAppTest) {
    // Default the update interval to 60 seconds if not supplied in configuration file.
    const updateIntervalSeconds = Meteor.settings.systemStats.updateIntervalSeconds || 60;
    SyncedCron.add({
      name: 'Update the SystemStats collection with current collection counts',
      schedule(parser) {
        return parser.text(`every ${updateIntervalSeconds} seconds`); // Parser is a later.js parse object.
      },
      job() {
        SystemStats.updateCounts();
      },
    });
    console.log(`Starting SyncedCron to update System Stats every ${updateIntervalSeconds} seconds.`);
    SyncedCron.start();
  }
}

Meteor.startup(() => {
  startupSystemStatsCronjob();
});
