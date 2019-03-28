import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { Incidents } from './IncidentsCollection';


export const getIncidentsInRange = new ValidatedMethod({
    name: 'Incidents.getIncidentsInRange',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        boxIds: { type: Array, minCount: 1 },
        'boxIds.$': { type: String },
        startTime_ms: { type: Number },
        endTime_ms: { type: Number },
        classifications: { type: Array, minCount: 1 },
        'classifications.$': { type: String },
        ieee_durations: { type: Array, minCount: 1 },
        'ieee_durations.$': { type: String },
        annotations: { type: Array, optional: true },
        'annotations.$': { type: String },
    }).validator({ clean: true }),
    run({ boxIds, startTime_ms, endTime_ms, classifications, ieee_durations, annotations }) {
        if (Meteor.isServer) {
            const query = {
                start_timestamp_ms: { $gte: startTime_ms },
                end_timestamp_ms: { $lte: endTime_ms },
            };
            if (boxIds && boxIds.length && boxIds.indexOf('ALL') === -1) query.box_id = { $in: boxIds };
            if (classifications && classifications.length && classifications.indexOf('ALL') === -1) query.classifications = { $in: classifications };
            if (ieee_durations && ieee_durations.length && ieee_durations.indexOf('ALL') === -1) query.ieee_duration = { $in: ieee_durations };
            if (annotations && annotations.length) query.annotations = { $in: annotations };

            return Incidents.find(query).fetch();
        }
        return null;
    },
});

/** Returns the incident document of the given incident_id.
 * @param {Number} event_id: The event_id of the event to retrieve
 */
export const getIncidentByIncidentID = new ValidatedMethod({
    name: 'Incidents.getIncidentByIncidentID',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        incident_id: { type: Number },
    }).validator({ clean: true }),
    run({ incident_id }) {
        if (Meteor.isServer) {
            const incident = Incidents.findOne({ incident_id });
            if (!incident) throw new Meteor.Error('invalid-incident-id', `The incident ${incident_id} could not be found.`);
            return incident;
        }
        return null;
    },
});

/** Returns all Incidents that were derived from the same Event for the given incident_id.
 * @param {Number} incident_id: The incident_id to retrieve related Incidents for
 */
export const getIncidentsFromSameEvent = new ValidatedMethod({
  name: 'Incidents.getIncidentsFromSameEvent',
  mixins: [CallPromiseMixin],
  validate: new SimpleSchema({
    incident_id: { type: Number },
  }).validator({ clean: true }),
  run({ incident_id }) {
    if (Meteor.isServer) {
      const incident = Incidents.findOne({ incident_id });
      if (!incident) throw new Meteor.Error('invalid-incident-id', `The incident ${incident_id} could not be found.`);
      if (incident.event_id < 0) return [];
      const incidents = Incidents.find({ event_id: incident.event_id })
          .fetch()
          .filter(incid => incid.incident_id !== incident_id);
      return incidents;
    }
    return null;
  },
});

/** Returns all Incidents that were derived from the given event_id.
 * @param {Number} event_id: The event_id to retrieve Incidents for
 */
export const getIncidentsFromEventID = new ValidatedMethod({
  name: 'Incidents.getIncidentsFromEventID',
  mixins: [CallPromiseMixin],
  validate: new SimpleSchema({
    event_id: { type: Number },
  }).validator({ clean: true }),
  run({ event_id }) {
    if (Meteor.isServer) {
      return Incidents.find({ event_id }).fetch();
    }
    return null;
  },
});
