import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/littledata:synced-cron';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

// This call to SyncedCron.config should exist in only one place. Here! Don't copy this code to other files.
// Logging defaults to off unless explicitly enabled.
SyncedCron.config({
  log: (Meteor.settings.syncedCron && Meteor.settings.syncedCron.logging) || false,
});

function startupSystemStatsCronjob() {
  // Only set up Cron Job when not in Test mode.
  if (!Meteor.isTest && !Meteor.isAppTest) {
    // Default the update interval to 59 seconds if not supplied in configuration file.
    const updateIntervalSeconds = Meteor.settings.systemStats ? Meteor.settings.systemStats.updateIntervalSeconds : 59;
    SyncedCron.add({
      name: 'Update the SystemStats collection with current collection counts',
      schedule(parser) {
        return parser.text(`every ${updateIntervalSeconds} seconds`); // seconds must be between 1 and 59
      },
      job() {
        SystemStats.updateCounts();
      },
    });
    console.log(`Starting cron job to update system stats every ${updateIntervalSeconds} seconds.`);
    SyncedCron.start();
  }
}

Meteor.startup(() => {
  startupSystemStatsCronjob();
});
