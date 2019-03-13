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
