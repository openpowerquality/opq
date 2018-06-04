import { Meteor } from 'meteor/meteor';
import { check, Match } from 'meteor/check';
import SimpleSchema from 'simpl-schema';
import moment from 'moment/moment';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/**
 * The Events collection stores abnormal PQ data detected by the system.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#events}
 */
class EventsCollection extends BaseCollection {

  constructor() {
    super('events', new SimpleSchema({
      event_id: Number,
      type: String,
      description: String,
      boxes_triggered: [String],
      boxes_received: [String],
      target_event_start_timestamp_ms: Number,
      target_event_end_timestamp_ms: Number,
      latencies_ms: { type: Array, optional: true },
      'latencies_ms.$': Number,
    }));

    // Event Type classifications will eventually move to the Incident level.
    this.FREQUENCY_SAG_TYPE = 'FREQUENCY_SAG';
    this.FREQUENCY_SWELL_TYPE = 'FREQUENCY_SWELL';
    this.VOLTAGE_SAG_TYPE = 'VOLTAGE_SAG';
    this.VOLTAGE_SWELL_TYPE = 'VOLTAGE_SWELL';
    this.THD_TYPE = 'THD';
    this.OTHER_TYPE = 'OTHER';
    this.eventTypes = [this.FREQUENCY_SAG_TYPE, this.FREQUENCY_SWELL_TYPE, this.VOLTAGE_SAG_TYPE,
      this.VOLTAGE_SWELL_TYPE, this.THD_TYPE, this.OTHER_TYPE];

    this.publicationNames = {
      GET_EVENTS: 'get_events',
      GET_RECENT_EVENTS: 'get_recent_events',
    };

    if (Meteor.server) {
      this._collection.rawCollection().createIndex(
          { target_event_start_timestamp_ms: 1 },
          { background: true },
          );
      this._collection.rawCollection().createIndex(
          { event_id: 1 },
          { background: true, unique: true },
      );
    }
  }

  /**
   * Defines a new Event document.
   * @param {Number} event_id - The event's id value (not Mongo ID)
   * @param {String} type - The unix timestamp (millis) of the measurement. (Deprecated, now optional).
   * @param {String} description - The description of the event.
   * @param {String} boxes_triggered - The OPQBoxes from which data was requested for this event.
   * @param {String} boxes_received - The OPQBoxes from which data was received for this event.
   * @param {String} target_event_start_timestamp_ms - The time this event started. Anything acceptable to moment().
   * @param {String} target_event_end_timestamp_ms - The time this event ended. Anything acceptable to moment().
   * @param {Number} latencies_ms - Array of unix timestamps for the event. See docs for details.
   * @returns The newly created document ID.
   */
  define({ event_id, type, description, boxes_triggered, boxes_received, target_event_start_timestamp_ms,
    target_event_end_timestamp_ms, latencies_ms }) {
    // Allow start and end times to be anything acceptable to the moment() parser.
    target_event_start_timestamp_ms = moment(target_event_start_timestamp_ms).valueOf(); // eslint-disable-line
    target_event_end_timestamp_ms = moment(target_event_end_timestamp_ms).valueOf(); // eslint-disable-line
    // Make sure boxes_triggered contains valid box_ids.
    OpqBoxes.assertValidBoxIds(boxes_triggered);
    const docID = this._collection.insert({ event_id, type, description, boxes_triggered, boxes_received,
      target_event_start_timestamp_ms, target_event_end_timestamp_ms, latencies_ms });
    return docID;
  }

  /**
   * Defines all publications related to this collection.
   */
  publish() {
    if (Meteor.isServer) {
      const self = this;

      Meteor.publish(this.publicationNames.GET_EVENTS, function ({ startTime, endTime }) {
        check(startTime, Match.Maybe(Number));
        check(endTime, Match.Maybe(Number));
        const selector = self.queryConstructors().getEvents({ startTime, endTime });
        return self.find(selector);
      });

      Meteor.publish(this.publicationNames.GET_RECENT_EVENTS, function ({ numEvents, excludeOther }) {
        check(numEvents, Number);
        const query = excludeOther ? { type: { $ne: 'OTHER' } } : {};
        const events = self.find(query, { sort: { target_event_start_timestamp_ms: -1 }, limit: numEvents });
        return events;
      });
    }
  }

  /**
   * Supports the GET_EVENTS publication method.
   * @returns { Object } An object formatted for the publication optional object.
   */
  queryConstructors() { // eslint-disable-line class-methods-use-this
    return {
      getEvents({ startTime, endTime }) {
        check(startTime, Match.Maybe(Number));
        check(endTime, Match.Maybe(Number));

        const selector = {};
        if (startTime) selector.target_event_start_timestamp_ms = { $gte: startTime };
        if (endTime) selector.target_event_end_timestamp_ms = { $lte: endTime };

        return selector;
      },
    };
  }
}

/**
 * Provides the singleton instance of this class.
 * @type {EventsCollection}
 */
export const Events = new EventsCollection();
