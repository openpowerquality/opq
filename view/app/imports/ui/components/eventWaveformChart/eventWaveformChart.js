import { Template } from 'meteor/templating';
import { dataContextValidator } from '../../../utils/utils.js';
import { getEventDataFSData } from '../../../api/eventDataFS/EventDataFSCollectionMethods.js';
import Dygraph from 'dygraphs';
import './eventWaveformChart.html';

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
        return [index, val/calibConstant];
        // return `${index}, ${val/calibConstant}\n`;
      });

      // const joinedDyPlotPoints = ['Time, Voltage\n'].concat(dyPlotPoints).join('\n');

      const ctx = template.$('.dygraphEventWaveform').get(0); // Dygraphs requires the raw DOM element.

      // Dygraphs
      template.graph = new Dygraph(ctx, dyPlotPoints, {labels: ['Time', 'Voltage']});

      // Sync Graph
      Template.currentData().dygraphSync(template.graph);
    }

  });

});