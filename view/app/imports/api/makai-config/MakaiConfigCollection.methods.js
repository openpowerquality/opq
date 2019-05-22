import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { MakaiConfig } from '../makai-config/MakaiConfigCollection';

export const updateThreshold = new ValidatedMethod({
    name: 'MakaiConfig.updateThreshold',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({
        docId: { type: String, required: true },
        boxId: { type: String, required: true },
        thresholdPercentFrequencyLow: { type: Number, required: true },
        thresholdPercentFrequencyHigh: { type: Number, required: true },
        thresholdPercentVoltageLow: { type: Number, required: true },
        thresholdPercentVoltageHigh: { type: Number, required: true },
        thresholdPercentThdHigh: { type: Number, required: true },
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
