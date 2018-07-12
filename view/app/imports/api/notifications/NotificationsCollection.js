import _ from 'lodash';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

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
      data: String,
      delivered: Boolean,
    }));
    this.notificationTypes = ['system service down'];
  }

  define({ username, type, timestamp, data, delivered = false }) {
    const docID = this._collection.insert({ username, type, data, delivered, timestamp });
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
