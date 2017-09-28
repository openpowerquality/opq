import { Template } from 'meteor/templating';
import { EventMetaData } from '../../../api/eventMetaData/EventMetaDataCollection.js';
import Chartjs from 'chart.js';
import Moment from 'moment';
import { Random } from 'meteor/random';
import { filterFormSchema } from "../../../utils/schemas.js";
import { dataContextValidator } from "../../../utils/utils.js";

// Templates and Sub-Template Inclusions
import './eventCountChart.html';



Template.eventCountChart.onCreated(function () {
  const template = this;

  dataContextValidator(template, new SimpleSchema({
    filters: {type: filterFormSchema, optional: true} // Optional because data context not available immediately.
  }), null);

  template.eventCountChart = null;
  template.currentDay = new ReactiveVar();

  // Set currentDay reactive var.
  template.autorun(() => {
    const dataContext = Template.currentData();
    (dataContext && dataContext.filters) ? template.currentDay.set(dataContext.filters.dayPicker)
                                         : template.currentDay.set(Moment().valueOf());
  });

  // Subscription
  template.autorun(() => {
    const currentDay = template.currentDay.get();
    if (currentDay) {
      const startOfDay = Moment(currentDay).startOf('day').valueOf(); // Ensure selected day is start of day timestamp.
      const endOfDay = Moment(currentDay).endOf('day').valueOf();
      template.subscribe(EventMetaData.publicationNames.GET_EVENT_META_DATA, {startTime: startOfDay, endTime: endOfDay});
    }
  });
});

Template.eventCountChart.onRendered(function () {
  const template = this;

  // Chart to display recent event counts by device id. Group into hours, max 24 hours.
  template.autorun(() => {
    // Ignore the 24th hour so it doesn't get grouped with the current hour.
    const currentDay = template.currentDay.get();
    if (currentDay) {
      const startOfDay = Moment(currentDay).startOf('day').valueOf(); // Ensure selected day is start of day timestamp.
      const endOfDay = Moment(currentDay).endOf('day').valueOf();
      const eventMetaDataSelector = EventMetaData.queryConstructors().getEventMetaData({startTime: startOfDay, endTime: endOfDay});
      const eventMetaData = EventMetaData.find(eventMetaDataSelector, {sort: {event_end: -1}});

      // Calculate labels. Floor of current hour, then get last 23 hours.
      const currHour = new Date().getHours();
      const hours = [];
      for (let i = 0; i < 24; i++) {
        const hour = currHour - i;
        (hour < 0) ? hours.push(24 + hour) : hours.push(hour);
      }
      hours.reverse(); // Reverse array in-place, so that most recent hour is at the end of the array.

      // Count events. Place into 1 hour groups per deviceId.
      const eventCountMap = {};
      eventMetaData.forEach(event => {
        const hour = new Date(event.event_end).getHours();

        // Note that we are only counting the initial triggering device so that our event count matches the calendar count.
        // If we later decide to count all boxes_triggered per event, just uncomment the forEach block below.
        const box_id = event.boxes_triggered[0];
        // event.boxes_triggered.forEach(box_id => {
          // Check for deviceId.
          if (eventCountMap[box_id]) {
            // Update hour count.
            (eventCountMap[box_id][hour]) ? eventCountMap[box_id][hour]++ : eventCountMap[box_id][hour] = 1;
          } else {
            eventCountMap[box_id] = {[hour]: 1}; // Create new object to keep track of hour count.
          }
        // });
      });

      // Create dataset
      const colors = ['rgb(167,197,189)', 'rgb(229,221,203)', 'rgb(235,123,89)', 'rgb(207,70,71)', 'rgb(82,70,86)'];
      const chartDatasets = [];
      Object.keys(eventCountMap).forEach(deviceId => {
        const dataset = {};
        dataset.label = `Device ${deviceId}`;
        dataset.backgroundColor = Random.choice(colors);
        dataset.data = hours.map(hour => eventCountMap[deviceId][hour]);
        chartDatasets.push(dataset);
      });

      // Create chart
      const ctx = template.$('#eventCountChart');
      if (template.eventCountChart) template.eventCountChart.destroy();
      template.eventCountChart = new Chartjs(ctx, {
        type: 'bar',
        data: {
          labels: hours,
          datasets: chartDatasets
        },
        options: {
          scales: {
            xAxes: [{
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: 'Hour of Day'
              }
            }],
            yAxes: [{
              ticks: {
                beginAtZero:true
              },
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: 'Event Count'
              }
            }]
          }
        }
      });
    }
  });
});