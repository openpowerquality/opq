import { Template } from 'meteor/templating';
import { dataContextValidator } from '../../../utils/utils.js';
import { getEventDataFSData } from '../../../api/eventDataFS/EventDataFSCollectionMethods.js';
import Dygraph from 'dygraphs';
import './eventWaveformChart.html';
import Moment from 'moment';

Template.eventWaveformChart.onCreated(function() {
  const template = this;

  dataContextValidator(template, new SimpleSchema({
    eventData: {type: Object, blackbox: true},
    dygraphSync: {type: Function}
  }), null);

});

Template.eventWaveformChart.onRendered(function() {
  const template = this;

  // Create Chart
  template.autorun(() => {
    const eventData = Template.currentData().eventData;

    if (eventData) {
      // Need to store these values in db.
      const boxCalibrationConstants = {
        1: 152.1,
        3: 154.20,
        4: 146.46
      };

      const calibConstant = boxCalibrationConstants[eventData.box_id] || 1;

      const dyPlotPoints = eventData.waveform.map((val, index) => {
        const timestamp = eventData.event_start + (index * (1.0/12.0));
        return [timestamp, val/calibConstant];
      });

      const ctx = template.$('.dygraphEventWaveform').get(0); // Dygraphs requires the raw DOM element.

      // Dygraphs
      template.graph = new Dygraph(ctx, dyPlotPoints, {
        labels: ['Timestamp', 'Voltage'],
        axes: {
          x: {
            valueFormatter: (millis, opts, seriesName, dygraph, row, col) => {
              // We must separately calculate the microseconds and concatenate it to the date string.
              return Moment(millis).format('[[]MM-DD-YYYY[]] HH:mm:ss.SSS').toString() + ((row * (1.0/12.0)) % 1).toFixed(3).substring(2);
            },
            axisLabelFormatter: (timestamp) => {
              return Moment(timestamp).format('HH:mm:ss.SSS');
            }
          }
        }

      });

      // Sync Graph
      Template.currentData().dygraphSync(template.graph);
    }

  });

});