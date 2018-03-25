import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

SyncedCron.config({
  // Log job run details to console
  log: false,
});

function startupSystemStatsCronjob() {
  // Default the update interval to 60 seconds.
  const updateIntervalSeconds = Meteor.settings.systemStatsUpdateIntervalSeconds || 60;
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

Meteor.startup(() => {
  startupSystemStatsCronjob();
});
