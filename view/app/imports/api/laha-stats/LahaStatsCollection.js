import SimpleSchema from 'simpl-schema';
import BaseCollection from '../base/BaseCollection.js';

const PluginStatsSchemaInner = new SimpleSchema({
    messages_received: Number,
    messages_published: Number,
    bytes_received: Number,
    bytes_published: Number
});

const PluginStatsSchema = new SimpleSchema({
    MakaiEventPlugin: PluginStatsSchemaInner,
    ThdPlugin: PluginStatsSchemaInner,
    StatusPlugin: PluginStatsSchemaInner,
    IticPlugin: PluginStatsSchemaInner,
    FrequencyVariationPlugin: PluginStatsSchemaInner,
    TransientPlugin: PluginStatsSchemaInner,
    Ieee1159VoltagePlugin: PluginStatsSchemaInner,
    SemiF47Plugin: PluginStatsSchemaInner,
    SystemStatsPlugin: PluginStatsSchemaInner,
    OutagePlugin: PluginStatsSchemaInner,
    LahaGcPlugin: PluginStatsSchemaInner
});

const DescriptiveStatisticSchema = new SimpleSchema({
    min: Number,
    max : Number,
    mean : Number,
    var : Number,
    cnt : Number,
    start_timestamp_s : Number,
    end_timestamp_s : Number
});

const SystemStatsSchema = new SimpleSchema({
    cpu_load_percent: DescriptiveStatisticSchema,
    memory_use_bytes: DescriptiveStatisticSchema,
    disk_use_bytes: DescriptiveStatisticSchema
});

const LahaLevelStatisticsSchema = new SimpleSchema({

});

/**
 * The laha-stats collection contains metrics generated by OPQ Mauka about plugins, system metrics, and Laha metrics.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html}
 */
class LahaStatsCollection extends BaseCollection {
    constructor() {
        super('laha_stats', new SimpleSchema({
            timestamp_s: Number,
            plugin_stats: PluginStatsSchema,
            system_stats: SystemStatsSchema,
            // laha_stats : {
            //     instantaneous_measurements_stats : {
            //         box_samples : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         }
            //     },
            //     aggregate_measurements_stats : {
            //         measurements : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         },
            //         trends : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         }
            //     },
            //     detections_stats : {
            //         events : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         }
            //     },
            //     incidents_stats : {
            //         incidents : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         }
            //     },
            //     phenomena_stats : {
            //         phenomena : {
            //             ttl : Number,
            //             count : Number,
            //             size_bytes : Number
            //         }
            //     },
            //     gc_stats : {
            //         samples : Number,
            //         measurements : Number,
            //         trends : Number,
            //         events : Number,
            //         incidents : Number,
            //         phenomena: Number
            //     },
            //     active_devices : Number
            // },
            // other_stats : {
            //     ground_truth : {
            //         count : Number,
            //         size_bytes : Number
            //     }
            // }
        }));
    }
}

/**
 * Provides the singleton instance of this class.
 * @type {LahaStatsCollection}
 */
export const LahaStats = new LahaStatsCollection();