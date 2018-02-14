import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

function startupSystemStatsCronjob() {
  // const updateIntervalSeconds = Meteor.settings.public.systemStatsUpdateIntervalSeconds.toString();
  SyncedCron.add({
    name: 'Update the SystemStats collection with current collection counts',
    schedule(parser) {
      return parser.text(`every 10 seconds`); // Parser is a later.js parse object.
      // return parser.text(`every ${updateIntervalSeconds} seconds`); // Parser is a later.js parse object.
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
