import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

const TtlsSchema = new SimpleSchema({
    box_samples: Number,
    measurements: Number,
    trends: Number,
    events: Number,
    incidents: Number,
});

/**
 * The laha_config collection contains configuration options for Laha, including default TTL values.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html}
 */
class LahaConfigCollection extends BaseCollection {
    constructor() {
        super('laha_config', new SimpleSchema({
            ttls: TtlsSchema,
        }));
    }
}

/**
 * Provides the singleton instance of this class.
 * @type {LahaConfigCollection}
 */
export const LahaConfig = new LahaConfigCollection();
