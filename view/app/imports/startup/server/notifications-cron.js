import { Meteor } from 'meteor/meteor';
import { SyncedCron } from 'meteor/percolate:synced-cron';
import { Email } from 'meteor/email';
import _ from 'lodash';
import { SSR } from 'meteor/meteorhacks:ssr';
import { Notifications } from '../../api/notifications/NotificationsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

SSR.compileTemplate('htmlEmail', Assets.getText('email-format.html'));

SyncedCron.config({
  log: Meteor.settings.syncedCronLogging,
});

function sendEmail(recipients, notifications, firstName) {
  Email.send({
    to: recipients,
    from: 'Open Power Quality <postmaster@mail.openpowerquality.org>',
    subject: 'You have new notifications',
    html: SSR.render('htmlEmail', { firstName: firstName, notifications: notifications }),
  });
}

/**
 * Checks userProfiles for amount of times a user wants to be notified in a day
 * Sends out the emails
 * Updates the sent notification documents 'delivered' field to true
 * @param maxDeliveries
 */
function findUsersAndSend(maxDeliveries) {
  const usersInterested = UserProfiles.find({ 'notification_preferences.max_per_day': maxDeliveries }).fetch();
  _.forEach(usersInterested, user => {
    const notifications = Notifications.find({ username: user.username, delivered: false }).fetch();
    const name = user.firstName;
    if (notifications.length !== 0) {
      const recipients = UserProfiles.getRecipients(user);
      sendEmail(recipients, notifications, name);
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

Meteor.startup(() => {
  if (Meteor.isProduction) {
    /**
     * sets the MAIL_URL environment variable to enable emails
     * MAIL_URL settings are only found in the settings.production.json file
     * https://docs.meteor.com/api/email.html
     */
    process.env.MAIL_URL = Meteor.settings.env.MAIL_URL;
    startupHourlyNotifications();
    startupDailyNotifications();
  }
});
