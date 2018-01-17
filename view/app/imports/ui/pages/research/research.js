import { Template } from 'meteor/templating';
import Chartjs from 'chart.js';
// import { EventMetaData } from '../../../api/events/EventsCollection.js';
// import { BoxEvents } from '../../../api/box-events/BoxEventsCollection.js';
// import { getRecentEventDataReqIds } from '../../../api/box-events/BoxEventsCollectionMethods.js';
import { getEventMeasurements } from '../../../api/measurements/MeasurementsCollectionMethods.js';

// Templates and Sub-Template Inclusions
import './research.html';
import '../../components/liveMeasurements/liveMeasurements.js';
import '../../components/eventCountChart/eventCountChart.js';
import '../../components/filterForm/filterForm.js';
import '../../components/eventList/eventList.js';
import '../../components/eventView/eventView.js';


Template.research.onCreated(function () {
  // const template = this;
});

Template.research.onRendered(function () {
  const template = this;

  // Enable Semantic-UI toggle styled checkbox.
  template.$('.ui.checkbox').checkbox();

  // Setup eventCountChart filter form popup
  template.$('#eventCountChartFiltersButton').popup({
    popup: template.$('#eventCountChartFiltersPopup'),
    on: 'click',
    position: 'bottom right',
    lastResort: true,
    closable: false, // Need this because popup is closing on flatpickr usage.
  });

  // Setup eventList filter form popup
  template.$('#eventListFiltersButton').popup({
    popup: template.$('#eventListFiltersPopup'),
    on: 'click',
    position: 'bottom right',
    lastResort: true,
    closable: false, // Need this because popup is closing on flatpickr usage.
  });

  // Plot selected event Vrms. Only plots the first device listed in boxes_received (see the method call for details).
  template.autorun(() => {
    // eslint-disable-next-line dot-notation
    const selectedEventId = (template.dataSources && template.dataSources['eventListSelectedEvent'])
        ? template.dataSources['eventListSelectedEvent'].get() // eslint-disable-line dot-notation
        : null;

    if (selectedEventId) {
      // eslint-disable-next-line max-len
      getEventMeasurements.call({ eventMetaDataId: selectedEventId }, (err, { eventMeasurements, precedingMeasurements, proceedingMeasurements }) => {
        if (err) {
          console.log(err); // eslint-disable-line no-console
        } else {
          // Ensure measurements are sorted in asc order (newest events at end of array).
          eventMeasurements.sort((a, b) => a.timestamp_ms - b.timestamp_ms);

          precedingMeasurements.sort((a, b) => a.timestamp_ms - b.timestamp_ms);

          proceedingMeasurements.sort((a, b) => a.timestamp_ms - b.timestamp_ms);

          // Format data for chart.
          /* eslint-disable arrow-body-style */
          const eventMeasurementsChartData = eventMeasurements.map(msr => {
            return { x: new Date(msr.timestamp_ms), y: msr.voltage };
          });

          const precedingMeasurementsChartData = precedingMeasurements.map(msr => {
            return { x: new Date(msr.timestamp_ms), y: msr.voltage };
          });

          const proceedingMeasurementsChartData = proceedingMeasurements.map(msr => {
            return { x: new Date(msr.timestamp_ms), y: msr.voltage };
          });
          /* eslint-enable arrow-body-style */


          // Create Chart
          const ctx = template.$('#selectedEventMeasurements');
          if (template.selectedEventMeasurements) template.selectedEventMeasurements.destroy();
          template.selectedEventMeasurements = new Chartjs(ctx, {
            type: 'line',
            data: {
              datasets: [{
                borderColor: '#ed8e53',
                fill: false,
                data: eventMeasurementsChartData,
                pointRadius: 0,
                tension: 0,
              }, {
                borderColor: '#EEC751',
                fill: false,
                data: precedingMeasurementsChartData,
                pointRadius: 0,
                tension: 0,
              }, {
                borderColor: '#EEC751',
                fill: false,
                data: proceedingMeasurementsChartData,
                pointRadius: 0,
                tension: 0,
              }],
            },
            options: {
              legend: {
                display: false,
              },
              title: {
                display: true,
                text: 'Vrms Measurements',
              },
              scales: {
                xAxes: [{
                  type: 'time',
                  display: true,
                  scaleLabel: {
                    display: true,
                    labelString: 'Timestamp',
                  },
                }],
                yAxes: [{
                  display: true,
                  scaleLabel: {
                    display: true,
                    labelString: 'Voltage',
                  },
                }],
              },
            },
          });
        }
      });
    }
  });
});

Template.research.helpers({

});

Template.research.events({

});
