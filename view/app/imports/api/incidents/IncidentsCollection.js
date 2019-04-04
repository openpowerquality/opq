import SimpleSchema from 'simpl-schema';
import moment from 'moment/moment';
import BaseCollection from '../base/BaseCollection.js';
import { OpqBoxes } from '../opq-boxes/OpqBoxesCollection';

/**
 * The Incidents collection stores documents that classify one or more incidents.
 * @see {@link https://openpowerquality.org/docs/cloud-datamodel.html#incidents}
 */
class IncidentsCollection extends BaseCollection {

    constructor() {
        super('incidents', new SimpleSchema({
            incident_id: Number,
            event_id: String,
            box_id: String,
            start_timestamp_ms: Number,
            end_timestamp_ms: Number,
            location: String,
            measurement_type: String,
            deviation_from_nominal: Number,
            measurements: [Object],
            gridfs_filename: String,
            classifications: [String],
            ieee_duration: String,
            annotations: [String],
            metadata: Object,
        }));

        // Classification Types
        this.EXCESSIVE_THD_TYPE = 'EXCESSIVE_THD';
        this.ITIC_PROHIBITED_TYPE = 'ITIC_PROHIBITED';
        this.ITIC_NO_DAMAGE_TYPE = 'ITIC_NO_DAMAGE';
        this.VOLTAGE_SWELL_TYPE = 'VOLTAGE_SWELL';
        this.VOLTAGE_SAG_TYPE = 'VOLTAGE_SAG';
        this.VOLTAGE_INTERRUPTION_TYPE = 'VOLTAGE_INTERRUPTION';
        this.FREQUENCY_SWELL_TYPE = 'FREQUENCY_SWELL';
        this.FREQUENCY_SAG_TYPE = 'FREQUENCY_SAG';
        this.FREQUENCY_INTERRUPTION_TYPE = 'FREQUENCY_INTERRUPTION';
        this.SEMI_F47_VIOLATION_TYPE = 'SEMI_F47_VIOLATION';
        this.OUTAGE_TYPE = 'OUTAGE';

        this.classificationTypes = [this.EXCESSIVE_THD_TYPE, this.ITIC_PROHIBITED_TYPE, this.ITIC_NO_DAMAGE_TYPE,
          this.VOLTAGE_SWELL_TYPE, this.VOLTAGE_SAG_TYPE, this.VOLTAGE_INTERRUPTION_TYPE, this.FREQUENCY_SWELL_TYPE,
          this.FREQUENCY_SAG_TYPE, this.FREQUENCY_INTERRUPTION_TYPE, this.SEMI_F47_VIOLATION_TYPE, this.OUTAGE_TYPE];

        // IEEE Duration Types
        this.INSTANTANEOUS_DURATION = 'INSTANTANEOUS';
        this.MOMENTARY_DURATION = 'MOMENTARY';
        this.TEMPORARY_DURATION = 'TEMPORARY';
        this.SUSTAINED_DURATION = 'SUSTAINED';

        this.ieeeDurationTypes = [this.INSTANTANEOUS_DURATION, this.MOMENTARY_DURATION, this.TEMPORARY_DURATION,
          this.SUSTAINED_DURATION];
    }

    /**
     * Defines a new Incident document.
     * @param {Number} incident_id - A unique integer representing the Incident.
     * @param {String} event_id - The Event id associated with the Incident.
     * @param {String} box_id - The OPQ Box id associated with the Incident.
     * @param {Number} start_timestamp_ms - Start time of the Incident (ms since epoch).
     * @param {Number} end_timestamp_ms - End time of the Incident (ms since epoch).
     * @param {String} location - The Location slug.
     * @param {String} measurement_type - One of VOLTAGE, FREQUENCY, THD, or TRANSIENT.
     * @param {Number} deviation_from_nominal - The absolute value of measurement deviation from nominal.
     * @param {Object[]} measurements - Copied from event.
     * @param {String} gridfs_filename - Filename of trimmed waveform copied from event.
     * @param {String[]} classifications - List of classifications that can be applied to Incident.
     * @param {String} ieee_duration - A string indicating one of the IEEE durations associated with this Incident.
     * @param {String[]} annotations - List of annotations associated with this Incident
     * @param {Object} metadata - Key-Value pairs providing meta-data for this Incident.
     * @returns The newly created document ID.
     */
    define({ incident_id, event_id, box_id, start_timestamp_ms, end_timestamp_ms, location, measurement_type,
                  deviation_from_nominal, measurements, gridfs_filename, classifications, ieee_duration, annotations,
                  metadata }) {
        // Allow start and end times to be anything acceptable to the moment() parser.
        start_timestamp_ms = moment(start_timestamp_ms).valueOf(); // eslint-disable-line
        end_timestamp_ms = moment(end_timestamp_ms).valueOf(); // eslint-disable-line

        // Make sure box_id is valid.
        OpqBoxes.assertValidBoxIds(box_id);
        const docID = this._collection.insert({ incident_id, event_id, box_id, start_timestamp_ms, end_timestamp_ms,
            location, measurement_type, deviation_from_nominal, measurements, gridfs_filename, classifications,
            ieee_duration, annotations, metadata });
        return docID;
    }
}

/**
 * Provides the singleton instance of this class.
 * @type {IncidentsCollection}
 */
export const Incidents = new IncidentsCollection();
