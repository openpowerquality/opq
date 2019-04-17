import _ from 'lodash';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { UserProfiles } from '../users/UserProfilesCollection';

/**
 * The OPQHealth service creates documents representing its findings on the current health of the system.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#health}
 */
class NotificationsCollection extends BaseCollection {

  constructor() {
    super('notifications', new SimpleSchema({
      username: String,
      type: String,
      timestamp: Date,
      data: Object,
      'data.summary': { type: String, optional: true },
      'data.service': { type: String, optional: true },
      delivered: Boolean,
    }));
    this.notificationTypes = ['system service down', 'new incident'];
  }

  define({ username, type, timestamp = new Date(), data, delivered = false }) {
    const docID = this._collection.insert({ username, type, data, delivered, timestamp });
    const userID = UserProfiles.findByUsername(username)._id;
    // When a new notification doc is created the user's unseen_notifications field turns true
    UserProfiles.update(userID, { unseen_notifications: true });
    return docID;
  }

  findNotificationsByUser(username) {
    return this._collection.find({ username }).fetch().reverse();
  }

  updateDeliveredStatus(notifications) {
    _.forEach(notifications, notification => {
      this._collection.update(notification._id, { $set: { delivered: true } });
    });
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {NotificationsCollection}
 */
export const Notifications = new NotificationsCollection();
