import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { FlowRouter } from 'meteor/kadira:flow-router';
import Moment from 'moment';
import Filesaver from 'file-saver';
import Papaparse from 'papaparse';
import _ from 'lodash';
import { getEventByEventID } from '../../../api/events/EventsCollectionMethods.js';
import { getBoxEvent } from '../../../api/box-events/BoxEventsCollectionMethods.js';
import { getEventData } from '../../../api/fs-files/FSFilesCollectionMethods';
// eslint-disable-next-line max-len
// import { getEventMeasurements, dygraphMergeDatasets } from '../../../api/measurements/MeasurementsCollectionMethods.js';
// import { getBoxCalibrationConstant } from '../../../api/opq-boxes/OpqBoxesCollectionMethods';
import '../../../../client/lib/misc/dygraphSynchronizer.js';
import './eventDetails.html';
import '../../components/eventWaveformChart/eventWaveformChart.js';
import '../../components/dygraph/dygraph.js';


Template.Event_Details_Page.onCreated(function () {
  const template = this;

  // dataContextValidator(template, new SimpleSchema({
  //   eventMetaDataId: {type: Mongo.ObjectID, optional: true} // Optional b/c waiting on user to select event.
  // }), null);
  template.event_id = FlowRouter.current().params.event_id;
  // console.log(template.event_id);

  template.currentEvent = new ReactiveVar(); // EventMetaData --> Events
  template.currentBoxEvents = new ReactiveVar([]); // EventData --> BoxEvents
  template.isLoadingEventData = new ReactiveVar(false);
  template.dygraphInstances = [];
  template.dygraphSync = null;

  // Retrieve document of given event meta data id.
  // template.autorun(() => {
  if (template.event_id) {
    // Clear old event data first.
    template.currentBoxEvents.set([]);

    // Then retrieve new meta data.
    template.isLoadingEventData.set(true);
    getEventByEventID.call({ event_id: template.event_id }, (error, eventMetaData) => {
      template.isLoadingEventData.set(false);
      if (error) {
        console.log(error);
      } else {
        template.currentEvent.set(eventMetaData);
      }
    });
  }
  // });

  // Retrieve event data for current event.
  template.autorun(() => {
    /* eslint-disable no-param-reassign, camelcase */
    const currentEvent = template.currentEvent.get();
    if (currentEvent) {
      const event_id = currentEvent.event_id;
      const boxes_received = currentEvent.boxes_received;

      boxes_received.forEach(box_id => {
        template.isLoadingEventData.set(true);
        getBoxEvent.call({ event_id, box_id }, (error, boxEvent) => {
          template.isLoadingEventData.set(false);
          if (error) {
            console.log(error);
          } else {
            // Now have to get waveform data from GridFs.
            template.isLoadingEventData.set(true);
            getEventData.call({ filename: boxEvent.data_fs_filename }, (err, waveformData) => {
              template.isLoadingEventData.set(false);
              if (err) {
                console.log(err);
              } else {
                boxEvent.waveform = waveformData;
                // Need to store these values in db.
                const boxCalibrationConstants = {
                  1: 152.1,
                  3: 154.20,
                  4: 146.46,
                };
                const constant = boxCalibrationConstants[boxEvent.box_id] || 1;
                const vrmsWindowValues = [];
                const SAMPLES_PER_CYCLE = 200;
                boxEvent.graphData = boxEvent.waveform.map((sample, index) => {
                  const timestamp = boxEvent.event_start_timestamp_ms + (index * (1.0 / 12.0));
                  const calibratedSample = sample / constant;

                  // Calculate Vrms. Note the RMS window size is equal to one cycle worth of samples.
                  if (vrmsWindowValues.push(calibratedSample) > SAMPLES_PER_CYCLE) vrmsWindowValues.shift();
                  // eslint-disable-next-line no-restricted-properties
                  const vSquaredSum = vrmsWindowValues.reduce((sum, curr) => sum + Math.pow(curr, 2));
                  const vRms = Math.sqrt(vSquaredSum / vrmsWindowValues.length);

                  return [timestamp, calibratedSample, vRms];
                });

                // Finally, we add to list of BoxEvents.
                const currentBoxEvents = template.currentBoxEvents.get();
                currentBoxEvents.push(boxEvent);
                template.currentBoxEvents.set(currentBoxEvents);
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
    const boxEvents = Template.instance().currentBoxEvents.get(); // Array of all event data.

    const modifiedBoxEvents = boxEvents.map(boxEvent => {
      // Add an event duration field. Calculation of duration has to be done this way because event_end_timestamp_ms
      // is currently incorect due to bug in Makai.
      // eslint-disable-next-line max-len, no-param-reassign
      boxEvent.duration = boxEvent.window_timestamps_ms[boxEvent.window_timestamps_ms.length - 1] - boxEvent.event_start_timestamp_ms;
      return boxEvent;
    });
    return modifiedBoxEvents;
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
    const event_id = event.currentTarget.dataset.event_id;
    const box_id = event.currentTarget.dataset.box_id;
    const export_type = event.currentTarget.dataset.export_type;

    console.log(export_type, event_id, box_id, event.currentTarget.dataset);
    console.log(typeof event_id);

    const boxEvents = instance.currentBoxEvents.get(); // Array of all event's boxEvents
    if (boxEvents) {
      const boxEvent = boxEvents.find(event => event.event_id === Number(event_id) // WAS HERE
          && event.box_id === Number(box_id));

      if (boxEvent) {
        boxEvent.waveformCalibrated = boxEvent.waveform.map((sample, index) => { // eslint-disable-line no-unused-vars
          // Need to store these values in db.
          const boxCalibrationConstants = {
            1: 152.1,
            3: 154.20,
            4: 146.46,
          };
          const constant = boxCalibrationConstants[boxEvent.box_id] || 1;
          // const timestamp = event.event_start_timestamp_ms + (index * (1.0 / 12.0));
          const calibratedSample = sample / constant;

          // return [timestamp, calibratedSample];
          return calibratedSample;
        });

        // eslint-disable-next-line max-len
        const eventPicked = _.pick(boxEvent, 'event_id', 'box_id', 'event_start_timestamp_ms', 'event_end_timestamp_ms', 'waveformCalibrated');
        if (export_type === 'json') {
          const json = JSON.stringify(eventPicked, null, 2);
          const blob = new Blob([json], { type: 'application/json; charset=utf-8' }); // eslint-disable-line no-undef
          Filesaver.saveAs(blob, `event-${eventPicked.event_id}-device-${eventPicked.box_id}`);
        } else if (export_type === 'csv') {
          const csv = Papaparse.unparse([eventPicked]);
          const blob = new Blob([csv], { type: 'text/csv; charset=utf-8' }); // eslint-disable-line no-undef
          Filesaver.saveAs(blob, `event-${eventPicked.event_id}-device-${eventPicked.box_id}`);
        }
      }
    }
    /* eslint-disable camelcase, no-console, no-shadow */
  },
});
