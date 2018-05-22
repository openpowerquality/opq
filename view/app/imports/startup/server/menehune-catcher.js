import { Meteor } from 'meteor/meteor';
import Moment from 'moment';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';

/**
 * OPQBox 2 keeps having its unplugged field set to true. We don't know why. This cron job is designed to determine
 * when the field gets set to true so we can try to determine why it happens.
 *
 * Once emilia's front page indicates that Box 2 is unplugged, then:
 *   * ssh into emilia.
 *   * invoke 'mongo' to bring up a shell.
 *   * invoke 'use opq' to get into the database.
 *   * invoke 'db.cronHistory.find({result: {$regex: 'MENEHUNE'}}).sort({startedAt: 1});'
 *   * The first entry is the first minute that box2 was observed to be unplugged.
 */
function startupMenehuneCatcherCronjob() {
  const updateIntervalSeconds = 60;
  SyncedCron.add({
    name: 'Catch the menehune who are setting OPQBox 2 to unplugged!',
    schedule(parser) {
      return parser.text(`every ${updateIntervalSeconds} seconds`); // Parser is a later.js parse object.
    },
    job() {
      const box2 = OpqBoxes.findBox('2');
      if (!box2) {
        return 'Box 2 not found';
      }
      const box2Unplugged = OpqBoxes.findBox('2').unplugged;
      const currentTime = Moment().format('lll');
      return `${currentTime}: ${box2Unplugged ? 'CAUGHT A MENEHUNE!!!!!!!!!!!!!!!!' : ''}`;
    },
  });
  console.log(`Starting MenehuneCatcher every ${updateIntervalSeconds} seconds.`);
  SyncedCron.start();
}

Meteor.startup(() => {
  startupMenehuneCatcherCronjob();
});
