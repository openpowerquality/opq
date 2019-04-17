import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/littledata:synced-cron';
import { Email } from 'meteor/email';
import _ from 'lodash';
import { SSR } from 'meteor/meteorhacks:ssr';
import { Notifications } from '../../api/notifications/NotificationsCollection';
import { Incidents } from '../../api/incidents/IncidentsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

SSR.compileTemplate('htmlEmail', Assets.getText('email-format.html'));
SSR.compileTemplate('notificationEmail', Assets.getText('notification-email-template.html'));

function sendEmail(contactEmails, startTime, services, downServiceTotal, incidentTotal, incidentTypes, incidentLocations) {
  Email.send({
    to: contactEmails,
    from: 'Open Power Quality <postmaster@mail.openpowerquality.org>',
    subject: 'New OPQ Notifications',
    html: SSR.render('notificationEmail', {
      startTime,
      services: Array.toString(services),
      downServiceTotal,
      incidentTotal,
      incidentTypes: Array.toString(incidentTypes),
      incidentLocations: Array.toString(incidentLocations),
    }),
  });
}

/**
 * Returns the list of services involved in the passed set of notifications.
 * @param notifications A list of notifications.
 * @returns {Array} An array of strings indicating the services.
 */
function extractServicesFromNotifications(notifications) {
  return _.unique(_.map(notifications, notification => notification.data.service));
}

/**
 * Checks userProfiles for amount of times a user wants to be notified in a day
 * Sends out the emails
 * Updates the sent notification documents 'delivered' field to true
 * @param maxDeliveries either 'once an hour' or 'once a day'
 */
function findUsersAndSend(maxDeliveries) {
  const usersInterested = UserProfiles.find({ 'notification_preferences.max_per_day': maxDeliveries }).fetch();
  const startTime = (maxDeliveries === 'once a day') ?
    Moment().subtract(1, 'day').format('LLLL') :
    Moment().subtract(1, 'hour').format('LLLL');

  // Now loop through all users desiring notifications, and compose and send the email(s).
  _.forEach(usersInterested, user => {
    const notifications = Notifications.find({ username: user.username, delivered: false }).fetch();
    const incidentReport = Incidents.getIncidentReport(startTime.valueOf());
    // only sends out an email if user has undelivered notifications
    if ((notifications.length > 0) || (incidentReport.totalIncidents > 0)) {
      const contactEmails = UserProfiles.getContactEmails(user._id);
      const services = extractServicesFromNotifications(notifications);
      const downServiceTotal = notifications.length;
      const incidentTotal = incidentReport.totalIncidents;
      const incidentType = incidentReport.

      sendEmail(contactEmails, startTime, services, downServiceTotal, incidentTotal, incidentTypes, incidentLocations);
      Notifications.updateDeliveredStatus(notifications);
      }
  });
}

// Schedules notification sending every hour on the hour
function startupHourlyNotifications() {
  // Only set up Cron Job when not in Test mode.
  if (!Meteor.isTest && !Meteor.isAppTest) {
    SyncedCron.add({
      name: 'Send out email alerts once an hour',
      schedule(parser) {
        return parser.text('every hour'); // Parser is a later.js parse object.
      },
      job() {
        findUsersAndSend('once an hour');
      },
    });
    console.log('Starting Hourly Notification Cron to check for undelivered notifications every hour');
    SyncedCron.start();
  }
}

// Schedules notification sending everyday at 6AM
function startupDailyNotifications() {
  // Only set up Cron Job when not in Test mode.
  if (!Meteor.isTest && !Meteor.isAppTest) {
    SyncedCron.add({
      name: 'Send out email alerts once a day',
      schedule(parser) {
        return parser.text('at 6:00 am'); // Parser is a later.js parse object.
      },
      job() {
        findUsersAndSend('once a day');
      },
    });
    console.log('Starting Daily Notification Cron to check for notifications every day at 6AM.');
    SyncedCron.start();
  }
}

// Finds notifications older than 2 days every hour and removes them from db
function removeOldNotifications() {
  // Only set up Cron Job when not in Test mode.
  if (!Meteor.isTest && !Meteor.isAppTest) {
    SyncedCron.add({
      name: 'Checks for notifications that are older than a week and removes them from db',
      schedule(parser) {
        return parser.text('every hour'); // Parser is a later.js parse object.
      },
      job() {
        const date = new Date(Date.now() - (8 * 24 * 60 * 60 * 1000));
        Notifications.remove({ timestamp: { $lt: date } });
      },
    });
    console.log('Starting Hourly Notification Cron to find notifications older than 48 hours');
    SyncedCron.start();
  }
}

Meteor.startup(() => {
  const testMode = Meteor.isTest || Meteor.isAppTest;
  const disabled = Meteor.settings.notificationCron && !Meteor.settings.notificationCron.enabled;
  const mailUrl = Meteor.settings.env && Meteor.settings.env.MAIL_URL;
  if (disabled) {
    console.log('Notification cron job disabled in view.config.json.');
  }
  if (!disabled && !mailUrl) {
    console.log('Notification cron job disabled due to missing Meteor.settings.env.MAIL_URL.');
  }
  if (!disabled && !testMode && mailUrl) {
    /** Set the MAIL_URL environment variable to enable emails */
    process.env.MAIL_URL = Meteor.settings.env.MAIL_URL;
    startupHourlyNotifications();
    startupDailyNotifications();
    removeOldNotifications();
  }
});
