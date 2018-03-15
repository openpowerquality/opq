import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

function startupSystemStatsCronjob() {
  // Default the update interval to 60 seconds.
  const updateIntervalSeconds = Meteor.settings.public.systemStatsUpdateIntervalSeconds || 60;
  SyncedCron.add({
    name: 'Update the SystemStats collection with current collection counts',
    schedule(parser) {
      return parser.text(`every ${updateIntervalSeconds} seconds`); // Parser is a later.js parse object.
    },
    job() {
      SystemStats.updateCounts();
    },
  });
  SyncedCron.start();
}

Meteor.startup(() => {
  startupSystemStatsCronjob();
});
