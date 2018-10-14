import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import _ from 'lodash';
import { Healths } from '../../api/health/HealthsCollection';
import { Notifications } from '../../api/notifications/NotificationsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

/**
 * serviceTracker sets a service name to true if the given service is down
 * therefore, multiple notifications docs won't be created if a service remains down
 * service name is set back to false if the given service is back up
 */
const serviceTracker = { mauka: false, makai: false, mongo: false, health: false };

/**
 * Creates a Notification document for everyone subscribed to the 'system service down' notification
 * when a service goes down
 * In order to not spam the user, the name of the service that is down
 * is set to true, and notifications for that service cannot be created again until
 * the service is back up
 */
function serviceHealthStatus(healths, service, usersInterested) {
  const serviceName = service.toLowerCase();
  const healthDoc = _.find(healths, health => health.service === service);
  if (healthDoc.status === 'DOWN' && serviceTracker[serviceName] === false) {
    _.forEach(usersInterested, user => {
      const username = user.username;
      const type = 'system service down';
      const dataSummary = { summary: `${service} service went down` };
      Notifications.define({ username, type, data: dataSummary });
      serviceTracker[serviceName] = true;
    });
  }
  if (healthDoc.status !== ('DOWN' || undefined) && serviceTracker[serviceName] === true) {
    serviceTracker[serviceName] = false;
  }
}

function healthCron() {
  // Only set up Cron Job when not in Test mode and enabled in settings file.
  if (!Meteor.isTest && !Meteor.isAppTest && Meteor.settings.healthCron.enabled === true) {
    // Default the update interval to 60 seconds if not supplied in configuration file.
    const updateIntervalSeconds = Meteor.settings.systemStats.updateIntervalSeconds || 60;
    const services = ['MAUKA', 'MAKAI', 'MONGO', 'HEALTH'];
    // eslint-disable-next-line
    const usersInterested = UserProfiles.find({ 'notification_preferences.notification_types': 'system service down' }).fetch();
    SyncedCron.add({
      name: 'Check Health collection for services that are down',
      schedule(parser) {
        return parser.text(`every ${updateIntervalSeconds} seconds`); // Parser is a later.js parse object.
      },
      job() {
        const healths = Healths.find(
            { timestamp: { $gt: new Date(Date.now() - (1000 * 62)) } },
            { sort: { timestamp: -1 } },
        ).fetch();
        _.map(services, service => serviceHealthStatus(healths, service, usersInterested));
      },
    });
    console.log(`Starting cron job to check health status every ${updateIntervalSeconds}`);
    SyncedCron.start();
  }
}

Meteor.startup(() => {
  healthCron();
});
