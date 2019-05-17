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
}

/**
 * Provides the singleton instance of this class.
 * @type {MakaiConfigCollection}
 */
export const MakaiConfig = new MakaiConfigCollection();
