import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { Incidents } from './IncidentsCollection';


export const getIncidentsInRange = new ValidatedMethod({
    name: 'Incidents.getIncidentsInRange',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        boxIds: { type: Array },
        'boxIds.$': { type: String },
        startTime_ms: { type: Number },
        endTime_ms: { type: Number },
    }).validator({ clean: true }),
    run({ boxIds, startTime_ms, endTime_ms }) {
        if (Meteor.isServer) {
            return Incidents.find({
                box_id: { $in: boxIds },
                start_timestamp_ms: { $gte: startTime_ms },
                end_timestamp_ms: { $lte: endTime_ms },
            }).fetch();
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

/** Returns all Incidents that originated from the same Event for the given incident_id.
 * @param {Number} event_id: The event_id of the event to retrieve
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
