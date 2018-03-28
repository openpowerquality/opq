import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { check, Match } from 'meteor/check';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';
import { progressBarSetup } from '../../modules/utils';

/**
 * Collection class for the events collection.
 * Docs: https://open-power-quality.gitbooks.io/open-power-quality-manual/content/datamodel/description.html#events
 */
class EventsCollection extends BaseCollection {

  /**
   * Creates the collection.
   */
  constructor() {
    super('events', new SimpleSchema({
      _id: { type: Mongo.ObjectID },
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

    this.publicationNames = {
      GET_EVENTS: 'get_events',
      GET_RECENT_EVENTS: 'get_recent_events',
    };
  }

  /**
   * Defines a new Event document.
   * @param {Number} event_id - The event's id value (not Mongo ID)
   * @param {String} type - The unix timestamp (millis) of the measurement.
   * @param {String} description - The description of the event.
   * @param {String} boxes_triggered - The OPQBoxes from which data was requested for this event.
   * @param {Number} latencies - Array of unix timestamps for the event. See docs for details.
   * @returns The newly created document ID.
   */
  define({ event_id, type, description, boxes_triggered, boxes_received, target_event_start_timestamp_ms,
    target_event_end_timestamp_ms, latencies_ms }) {
    const docID = this._collection.insert({ event_id, type, description, boxes_triggered, boxes_received,
      target_event_start_timestamp_ms, target_event_end_timestamp_ms, latencies_ms });
    return docID;
  }

  /**
   * Returns an object representing a single Event.
   * @param {Object} docID - The Mongo.ObjectID of the Event.
   * @returns {Object} - An object representing a single Event.
   */
  dumpOne(docID) {
    /* eslint-disable camelcase */
    const doc = this.findDoc(docID);
    const event_id = doc.event_id;
    const type = doc.type;
    const description = doc.description;
    const boxes_triggered = doc.boxes_triggered;
    const boxes_received = doc.boxes_received;
    const target_event_start_timestamp_ms = doc.target_event_start_timestamp_ms;
    const target_event_end_timestamp_ms = doc.target_event_end_timestamp_ms;
    const latencies_ms = doc.latencies_ms;

    return { event_id, type, description, boxes_triggered, boxes_received,
      target_event_start_timestamp_ms, target_event_end_timestamp_ms, latencies_ms };
    /* eslint-enable camelcase */
  }

  checkIntegrity() {
    const problems = [];
    const totalCount = this.count();
    const validationContext = this.getSchema().namedContext('eventsIntegrity');
    const pb = progressBarSetup(totalCount, 2000, `Checking ${this._collectionName} collection: `);

    this.find().forEach((doc, index) => {
      pb.updateBar(index); // Update progress bar.

      // Validate each document against the collection schema.
      validationContext.validate(doc);
      if (!validationContext.isValid()) {
        // eslint-disable-next-line max-len
        problems.push(`Events document failed schema validation: ${doc._id} (Invalid keys: ${JSON.stringify(validationContext.invalidKeys(), null, 2)})`);
      }
      validationContext.resetValidation();
    });

    pb.clearInterval();
    return problems;
  }


  /**
   * Loads all publications related to this collection.
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

      Meteor.publish(this.publicationNames.GET_RECENT_EVENTS, function ({ numEvents }) {
        check(numEvents, Number);

        const events = self.find({}, { sort: { timestamp_ms: -1 }, limit: numEvents });
        return events;
      });
    }
  }

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
