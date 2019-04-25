import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { LahaStats } from './LahaStatsCollection';

export const getLahaStatsInRange = new ValidatedMethod({
    name: 'LahaStats.getLahaStatsInRange',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        startTimestampS: { type: Number },
        endTimestampS: { type: Number },
    }).validator({ clean: true }),
    run({ startTimestampS, endTimestampS }) {
        if (Meteor.isServer) {
            const query = {
                timestamp_s: { $gte: startTimestampS,
                               $lte: endTimestampS },
            };

            return LahaStats.find(query).fetch();
        }
        return null;
    },
});
