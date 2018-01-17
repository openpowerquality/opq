import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { FlowRouter } from 'meteor/kadira:flow-router';
import Moment from 'moment';
import Filesaver from 'file-saver';
import Papaparse from 'papaparse';
import _ from 'lodash';
import { getEventMetaDataByEventNumber } from '../../../api/events/EventsCollectionMethods.js';
import { getEventData } from '../../../api/box-events/BoxEventsCollectionMethods.js';
import { getEventDataFSData } from '../../../api/eventDataFS/EventDataFSCollectionMethods.js';
import { getEventMeasurements, dygraphMergeDatasets } from '../../../api/measurements/MeasurementsCollectionMethods.js';
import '../../../../client/lib/misc/dygraphSynchronizer.js';
import './eventDetails.html';
import '../../components/eventWaveformChart/eventWaveformChart.js';
import '../../components/dygraph/dygraph.js';


Template.Event_Details_Page.onCreated(function () {
  const template = this;

  // dataContextValidator(template, new SimpleSchema({
  //   eventMetaDataId: {type: Mongo.ObjectID, optional: true} // Optional b/c waiting on user to select event.
  // }), null);
  template.event_number = FlowRouter.current().params.eventNumber;
  // console.log(template.event_number);

  template.currentEventMetaData = new ReactiveVar();
  template.currentEventData = new ReactiveVar([]);
  template.isLoadingEventData = new ReactiveVar(false);
  template.dygraphInstances = [];
  template.dygraphSync = null;

  // Retrieve document of given event meta data id.
  // template.autorun(() => {
  if (template.event_number) {
    // Clear old event data first.
    template.currentEventData.set([]);

    // Then retrieve new meta data.
    template.isLoadingEventData.set(true);
    getEventMetaDataByEventNumber.call({ event_number: template.event_number }, (error, eventMetaData) => {
      template.isLoadingEventData.set(false);
      if (error) {
        console.log(error);
      } else {
        template.currentEventMetaData.set(eventMetaData);
      }
    });
  }
  // });

  // Retrieve event data for current event.
  template.autorun(() => {
    /* eslint-disable no-param-reassign, camelcase */
    const currentEventMetaData = template.currentEventMetaData.get();
    if (currentEventMetaData) {
      const event_number = currentEventMetaData.event_number;
      const boxes_received = currentEventMetaData.boxes_received;

      boxes_received.forEach(box_id => {
        template.isLoadingEventData.set(true);
        getEventData.call({ event_number, box_id }, (error, eventData) => {
          template.isLoadingEventData.set(false);
          if (error) {
            console.log(error);
          } else {
            // Now have to get waveform data from GridFs.
            template.isLoadingEventData.set(true);
            getEventDataFSData.call({ filename: eventData.data }, (err, waveformData) => {
              template.isLoadingEventData.set(false);
              if (err) {
                console.log(err);
              } else {
                eventData.waveform = waveformData;
                // Need to store these values in db.
                const boxCalibrationConstants = {
                  1: 152.1,
                  3: 154.20,
                  4: 146.46,
                };
                const constant = boxCalibrationConstants[eventData.box_id] || 1;
                const vrmsWindowValues = [];
                const SAMPLES_PER_CYCLE = 200;
                eventData.graphData = eventData.waveform.map((sample, index) => {
                  const timestamp = eventData.event_start + (index * (1.0 / 12.0));
                  const calibratedSample = sample / constant;

                  // Calculate Vrms. Note the RMS window size is equal to one cycle worth of samples.
                  if (vrmsWindowValues.push(calibratedSample) > SAMPLES_PER_CYCLE) vrmsWindowValues.shift();
                  // eslint-disable-next-line no-restricted-properties
                  const vSquaredSum = vrmsWindowValues.reduce((sum, curr) => sum + Math.pow(curr, 2));
                  const vRms = Math.sqrt(vSquaredSum / vrmsWindowValues.length);

                  return [timestamp, calibratedSample, vRms];
                });

                // Finally get measurements (voltages/frequencies RMS) for each box
                template.isLoadingEventData.set(true);
                getEventMeasurements.call({
                  device_id: box_id,
                  startTime: eventData.event_start,
                  endTime: eventData.time_stamp[eventData.time_stamp.length - 1], // event_end is currently bugged.
                },
                (errors, { eventMeasurements, precedingMeasurements, proceedingMeasurements }) => {
                  template.isLoadingEventData.set(false);
                  if (errors) {
                    console.log(errors);
                  } else {
                    eventData.measurements = { eventMeasurements, precedingMeasurements, proceedingMeasurements };

                    const currentEventData = template.currentEventData.get();
                    currentEventData.push(eventData);
                    template.currentEventData.set(currentEventData);
                  }
                });
              }
            });
          }
        });
      });
    }
    /* eslint-enable no-param-reassign, camelcase */
  });
});

Template.Event_Details_Page.onRendered(function () {
  // const template = this;

  // template.$('#eventData-modal').modal(); // Init modal.
});

Template.Event_Details_Page.helpers({
  eventDatas() {
    const eventDataArr = Template.instance().currentEventData.get(); // Array of all event data.

    const modifiedEventData = eventDataArr.map((eventData) => {
      /* eslint-disable no-param-reassign, max-len */
      // Format RMS voltage and freq data for dygraphs.
      eventData.measurements.voltages = dygraphMergeDatasets('timestamp_ms', 'voltage', eventData.measurements.eventMeasurements, eventData.measurements.precedingMeasurements, eventData.measurements.proceedingMeasurements);
      eventData.measurements.frequencies = dygraphMergeDatasets('timestamp_ms', 'frequency', eventData.measurements.eventMeasurements, eventData.measurements.precedingMeasurements, eventData.measurements.proceedingMeasurements);

      // Add an event duration field
      eventData.duration = eventData.time_stamp[eventData.time_stamp.length - 1] - eventData.event_start;
      return eventData;
      /* eslint-enable no-param-reassign, max-len */
    });
    return modifiedEventData;
  },
  dygraphWaveformOptions() {
    // const template = Template.instance();

    return {
      labels: ['Timestamp', 'Voltage', 'Vrms'],
      axes: {
        x: {
          axisLabelWidth: 100, // Extra space needed due to the microseconds concat.
          // eslint-disable-next-line no-unused-vars, arrow-body-style
          valueFormatter: (millis, opts, seriesName, dygraph, row, col) => {
            // We must separately calculate the microseconds and concatenate it to the date string.
            return Moment(millis).format('[[]MM-DD-YYYY[]] HH:mm:ss.SSS').toString()
                + ((row * (1.0 / 12.0)) % 1).toFixed(3).substring(2);
          },
          axisLabelFormatter: (timestamp) => Moment(timestamp).format('HH:mm:ss.SSS'),
        },
        y: {
          axisLabelWidth: 30,
        },
      },
    };
  },
  dygraphRMSOptions(yLabel) {
    return {
      // eslint-disable-next-line prefer-template
      labels: ['Timestamp', yLabel, yLabel + '(pre)', yLabel + '(post)'], // Legend labels
      colors: ['red', '#EEC751', '#EEC751'],
      ylabel: yLabel,
      axes: {
        x: {
          pixelsPerLabel: 45,
          // eslint-disable-next-line no-unused-vars, arrow-body-style
          valueFormatter: (millis, opts, seriesName, dygraph, row, col) => {
            // We must separately calculate the microseconds and concatenate it to the date string.
            return Moment(millis).format('HH:mm:ss.SSS').toString();
          },
          axisLabelFormatter: (timestamp) => Moment(timestamp).format('HH:mm:ss'),
        },
        y: {
          axisLabelWidth: 55,
          pixelsPerLabel: 15,
        },
      },
    };
  },
  dygraphSynchronizer() {
    const template = Template.instance();
    template.isUpdatingGraphs = false; // Actually not really needed because will initially return as undefined/false
    const syncOpts = {
      enableXSync: true,
      enableYSync: false, // Not working as intended, keep false for now.
      enableHighlightSync: true,
    };

    const dygraphCallbacks = {
      drawCallback: function (graph, isInitial) {
        if (template.isUpdatingGraphs || isInitial) return;
        template.isUpdatingGraphs = true;

        // Get the selected x-axis range
        const selXAxisRange = graph.xAxisRange(); // [start, end]
        const selYRange = graph.yAxisRange(); // [bottom, top]
        const opts = {};
        if (syncOpts.enableXSync) opts.dateWindow = [selXAxisRange[0], selXAxisRange[1]];
        if (syncOpts.enableYSync) opts.valueRange = [selYRange[0], selYRange[1]];
        // Now we synchronize selected range across each graph.
        template.dygraphInstances.forEach(currGraph => {
          const currXAxisDataRange = currGraph.xAxisExtremes(); // The x-axis [min, max] of entire data set.

          // Reset graph if selected range goes outside of data set range (on both ends). This ensures that
          // each graph's x-axis range will never go beyond its data set range (on both ends; can still go beyond
          // on one end).
          if (selXAxisRange[0] < currXAxisDataRange[0] && selXAxisRange[1] > currXAxisDataRange[1]) {
            currGraph.resetZoom();
          } else {
            // Otherwise just set x-axis to the selected range.
            currGraph.updateOptions(opts);
          }
        });

        template.isUpdatingGraphs = false; // Can unblock after looping through graphs.
      },
      highlightCallback: function (event, x, points, row, seriesName) {
        if (template.isUpdatingGraphs) return; // Might have to create a separate boolean for this.
        template.isUpdatingGraphs = true;
        template.dygraphInstances.forEach(currGraph => {
          const index = currGraph.getRowForX(x);
          if (index !== null) {
            currGraph.setSelection(index, seriesName);
          }
        });
        template.isUpdatingGraphs = false;
      },
      unhighlightCallback: function (event) { // eslint-disable-line no-unused-vars
        if (template.isUpdatingGraphs) return; // Might have to create a separate boolean for this.
        template.isUpdatingGraphs = true;
        template.dygraphInstances.forEach(currGraph => currGraph.clearSelection());
        template.isUpdatingGraphs = false;
      },
    };

    // Remove unwanted sync callbacks.
    if (!syncOpts.enableXSync) delete dygraphCallbacks.drawCallback;
    if (!syncOpts.enableHighlightSync) {
      delete dygraphCallbacks.highlightCallback;
      delete dygraphCallbacks.unhighlightCallback;
    }

    return (graph) => {
      graph.updateOptions(dygraphCallbacks, true); // True b/c we are just updating opts and don't want redraw to occur.
      template.dygraphInstances.push(graph);
    };
  },
  calibratedWaveformData(boxId, waveformData) {
    // Need to store these values in db.
    const boxCalibrationConstants = {
      1: 152.1,
      3: 154.20,
      4: 146.46,
    };
    const constant = boxCalibrationConstants[boxId] || 1;
    const calibratedData = waveformData.map(val => val / constant);
    return calibratedData;
  },
  isLoadingEventData() {
    return Template.instance().isLoadingEventData.get();
  },
});

Template.Event_Details_Page.events({
  'click .ui.button': function (event, instance) {
    const boxId = event.currentTarget.id.replace('-button', '');
    instance.$(`#${boxId}-modal`).modal({ detachable: false }).modal('show');
  },
  'click .data-export': function (event, instance) {
    /* eslint-disable camelcase, no-console, no-shadow */
    event.preventDefault();
    const event_number = event.currentTarget.dataset.event_number;
    const box_id = event.currentTarget.dataset.box_id;
    const export_type = event.currentTarget.dataset.export_type;

    console.log(export_type, event_number, box_id, event.currentTarget.dataset);
    console.log(typeof event_number);

    const eventData = instance.currentEventData.get(); // Array of all event data.
    if (eventData) {
      const event = eventData.find(event => event.event_number === Number(event_number)
          && event.box_id === Number(box_id));

      if (event) {
        event.waveformCalibrated = event.waveform.map((sample, index) => { // eslint-disable-line no-unused-vars
          // Need to store these values in db.
          const boxCalibrationConstants = {
            1: 152.1,
            3: 154.20,
            4: 146.46,
          };
          const constant = boxCalibrationConstants[eventData.box_id] || 1;
          // const timestamp = event.event_start + (index * (1.0 / 12.0));
          const calibratedSample = sample / constant;

          // return [timestamp, calibratedSample];
          return calibratedSample;
        });

        const eventPicked = _.pick(event, 'event_number', 'box_id', 'event_start', 'event_end', 'waveformCalibrated');
        if (export_type === 'json') {
          const json = JSON.stringify(eventPicked, null, 2);
          const blob = new Blob([json], { type: 'application/json; charset=utf-8' }); // eslint-disable-line no-undef
          Filesaver.saveAs(blob, `event-${eventPicked.event_number}-device-${eventPicked.box_id}`);
        } else if (export_type === 'csv') {
          const csv = Papaparse.unparse([eventPicked]);
          const blob = new Blob([csv], { type: 'text/csv; charset=utf-8' }); // eslint-disable-line no-undef
          Filesaver.saveAs(blob, `event-${eventPicked.event_number}-device-${eventPicked.box_id}`);
        }
      }
    }
    /* eslint-disable camelcase, no-console, no-shadow */
  },
});
