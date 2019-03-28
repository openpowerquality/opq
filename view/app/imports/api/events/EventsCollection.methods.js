import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { Events } from './EventsCollection.js';
import { BoxEvents } from '../box-events/BoxEventsCollection';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/** Returns an array of events that were detected by specified boxes, in a specified range.
 * @param {String[]} boxIDs: List of box IDs to get data for
 * @param {Number} startDate_ms: Start of range in Unix epoch time
 * @param {Number} endDate_ms: End of range in Unix epoch time
 */
export const getEventsInRange = new ValidatedMethod({
  name: 'Events.getEventsInRange',
  mixins: [CallPromiseMixin],
  validate: new SimpleSchema({
    boxIDs: { type: Array },
    'boxIDs.$': { type: String },
    startTime_ms: { type: Number },
    endTime_ms: { type: Number },
  }).validator({ clean: true }),
  run({ boxIDs, startTime_ms, endTime_ms }) {
    if (Meteor.isServer) {
      return Events.find({
        boxes_triggered: { $in: boxIDs },
        target_event_start_timestamp_ms: { $gte: startTime_ms },
        target_event_end_timestamp_ms: { $lte: endTime_ms },
      }).fetch();
    }
    return null;
  },
});

/** Returns the event document of the given event_id.
 * @param {Number} event_id: The event_id of the event to retrieve
 */
export const getEventByEventID = new ValidatedMethod({
  name: 'Events.getEventByEventID',
  mixins: [CallPromiseMixin],
  validate: new SimpleSchema({
    event_id: { type: Number },
  }).validator({ clean: true }),
  run({ event_id }) {
    if (Meteor.isServer) {
      const event = Events.findOne({ event_id });
      if (!event) throw new Meteor.Error('invalid-event-id', `The event_id ${event_id} could not be found.`);
      return event;
    }
    return null;
  },
});

/** Helper function that returns an object containing all required information for displaying waveforms associated
 * with the given event_id.
 * @param {Number} event_id - The event_id to retrieve information for.
 */
export const getEventWaveformViewerData = new ValidatedMethod({
  name: 'Events.getEventWaveformViewerData',
  mixins: [CallPromiseMixin],
  validate: new SimpleSchema({
    event_id: { type: Number },
  }).validator({ clean: true }),
  run({ event_id }) {
    if (Meteor.isServer) {
      const event = Events.findOne({ event_id });
      if (!event) throw new Meteor.Error('invalid-event-id', `The event_id ${event_id} could not be found.`);

      // Each array element is {boxEvent, opqBox}
      const retObj = {
        event,
        triggeredBoxes: [],
        otherBoxes: [],
      };

      event.boxes_received.forEach(box_id => {
        const boxEvent = BoxEvents.findOne({ event_id, box_id });
        const opqBox = OpqBoxes.findOne({ box_id });
        if (boxEvent && opqBox) {
          if (event.boxes_triggered.indexOf(box_id) > -1) {
            retObj.triggeredBoxes.push({ boxEvent, opqBox });
          } else {
            retObj.otherBoxes.push({ boxEvent, opqBox });
          }
        }
      });

      return retObj;
    }
    return null;
  },
});
