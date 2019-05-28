import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { MakaiConfig } from '../makai-config/MakaiConfigCollection';

export const updateThreshold = new ValidatedMethod({
    name: 'MakaiConfig.updateThreshold',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        docId: { type: String },
        boxId: { type: String },
        thresholdPercentFrequencyLow: { type: Number },
        thresholdPercentFrequencyHigh: { type: Number },
        thresholdPercentVoltageLow: { type: Number },
        thresholdPercentVoltageHigh: { type: Number },
        thresholdPercentThdHigh: { type: Number },
    }).validator({ clean: true }),
    run({
            docId,
            boxId,
            thresholdPercentFrequencyLow,
            thresholdPercentFrequencyHigh,
            thresholdPercentVoltageLow,
            thresholdPercentVoltageHigh,
            thresholdPercentThdHigh,
    }) {
        if (Meteor.isServer) {
            return MakaiConfig.updateThresholds(
                docId,
                boxId,
                thresholdPercentFrequencyLow,
                thresholdPercentFrequencyHigh,
                thresholdPercentVoltageLow,
                thresholdPercentVoltageHigh,
                thresholdPercentThdHigh,
            );
        }
        return null;
    },
});
