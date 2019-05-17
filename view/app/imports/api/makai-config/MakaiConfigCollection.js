import { Meteor } from 'meteor/meteor';
import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

const TriggeringOverridesSchema = new SimpleSchema({
    box_id: String,
    ref_f: Number,
    ref_v: Number,
    threshold_percent_f_low: Number,
    threshold_percent_f_high: Number,
    threshold_percent_v_low: Number,
    threshold_percent_v_high: Number,
    threshold_percent_thd_high: Number,
});

const TriggeringSchema = new SimpleSchema({
    default_ref_f: Number,
    default_ref_v: Number,
    default_threshold_percent_f_low: Number,
    default_threshold_percent_f_high: Number,
    default_threshold_percent_v_low: Number,
    default_threshold_percent_v_high: Number,
    default_threshold_percent_thd_high: Number,
    triggering_overrides: TriggeringOverridesSchema,
});

/**
 * The makai_config collection contains configuration options for Makai including triggering thresholds.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html}
 */
class MakaiConfigCollection extends BaseCollection {
    constructor() {
        super('makai_config', new SimpleSchema({
            triggering: TriggeringSchema,
        }));
    }

    getMakaiConfig() {
        const makaiConfig = this._collection.findOne();
        if (makaiConfig) {
            return makaiConfig;
        }
        throw new Meteor.Error('MakaiConfig not found.');
    }

    getTriggeringConfig() {
        const makaiConfig = this.getMakaiConfig();
        if (makaiConfig.triggering) {
            return makaiConfig.triggering;
        }
        throw new Meteor.Error('MakaiConfig.triggering not found.');
    }

    getTriggeringOverrides() {
        const triggering = this.getTriggeringConfig();
        if (triggering.triggering_overrides) {
            return triggering.triggering_overrides;
        }
        throw new Meteor.Error('MakaiConfig.triggering.triggering_overrides not found.');
    }

    getTriggeringOverrideOrDefault(box_id) {
        const overrides = this.getTriggeringOverrides();
        let foundOverride = null;
        overrides.forEach(function(override) {
            if (override.box_id === box_id) {
                foundOverride = override;
            }
        });
        if (foundOverride !== null) {
           return {
               ref_f: foundOverride.ref_f,
               ref_v: foundOverride.ref_v,
               threshold_percent_f_low: foundOverride.threshold_percent_f_low,
               threshold_percent_f_high: foundOverride.threshold_percent_f_high,
               threshold_percent_v_low: foundOverride.threshold_percent_v_low,
               threshold_percent_v_high: foundOverride.threshold_percent_v_high,
               threshold_percent_thd_high: foundOverride.threshold_percent_thd_high,
           };
        }
        const triggering = this.getTriggeringConfig();
        return {
            ref_f: triggering.default_ref_f,
            ref_v: triggering.default_ref_v,
            threshold_percent_f_low: triggering.default_threshold_percent_f_low,
            threshold_percent_f_high: triggering.default_threshold_percent_f_high,
            threshold_percent_v_low: triggering.default_threshold_percent_v_low,
            threshold_percent_v_high: triggering.default_threshold_percent_v_high,
            threshold_percent_thd_high: triggering.default_threshold_percent_thd_high,
        };
    }
}

/**
 * Provides the singleton instance of this class.
 * @type {MakaiConfigCollection}
 */
export const MakaiConfig = new MakaiConfigCollection();
