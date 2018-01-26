import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import Chartjs from 'chart.js';
import Moment from 'moment';
import { Events } from '../../../api/events/EventsCollection';
import { filterFormSchema } from '../../../utils/schemas.js';
import { dataContextValidator } from '../../../utils/utils.js';
import { ReactiveVarHelper } from '../../../modules/ReactiveVarHelper';

// Templates and Sub-Template Inclusions
import './eventCountChart.html';


Template.eventCountChart.onCreated(function () {
  const template = this;

  // Validate data context
  dataContextValidator(template, new SimpleSchema({
    filters: { type: filterFormSchema, optional: true }, // Optional because data context not available immediately.
    filtersRV: { type: ReactiveVarHelper },
  }), null);

  template.eventCountChart = null;
  template.currentDay = new ReactiveVar(Moment().valueOf()); // Default day is current day.

  // Register callback to update currently set day whenever it's set from the filter form.
  template.data.filtersRV.onChange(newFilters => {
    template.currentDay.set(newFilters.dayPicker);
  });

  // Subscription
  template.autorun(() => {
    const currentDay = template.currentDay.get();
    if (currentDay) {
      const startOfDay = Moment(currentDay).startOf('day').valueOf(); // Ensure selected day is start of day timestamp.
      const endOfDay = Moment(currentDay).endOf('day').valueOf();
      template.subscribe(Events.publicationNames.GET_EVENTS, {
        startTime: startOfDay,
        endTime: endOfDay,
      });
    }
  });
});

Template.eventCountChart.onRendered(function () {
  const template = this;

  // Chart to display recent event counts by device id. Group into hours, max 24 hours.
  template.autorun(() => {
    // Ignore the 24th hour so it doesn't get grouped with the current hour.
    const currentDay = template.currentDay.get();
    if (currentDay && template.subscriptionsReady()) {
      const startOfDay = Moment(currentDay).startOf('day').valueOf(); // Ensure selected day is start of day timestamp.
      const endOfDay = Moment(currentDay).endOf('day').valueOf();
      const eventsSelector = Events.queryConstructors().getEvents({
        startTime: startOfDay,
        endTime: endOfDay,
      });
      const events = Events.find(eventsSelector, { sort: { target_event_end_timestamp_ms: -1 } });

      // Calculate labels. Floor of current hour, then get last 23 hours.
      const currHour = new Date().getHours();
      const hours = [];
      for (let i = 0; i < 24; i++) {
        const hour = currHour - i;
        if (hour < 0) {
          hours.push(24 + hour);
        } else {
          hours.push(hour);
        }
      }
      hours.reverse(); // Reverse array in-place, so that most recent hour is at the end of the array.

      // Count events. Place into 1 hour groups per deviceId.
      const eventCountMap = {};
      events.forEach(event => {
        const hour = new Date(event.target_event_end_timestamp_ms).getHours();

        // Note that we are only counting the initial triggering device so that our event count matches the calendar
        // count. If we later decide to count all boxes_triggered per event, just uncomment the forEach block below.
        const boxId = event.boxes_triggered[0];
        // event.boxes_triggered.forEach(box_id => {
        // Check for deviceId.
        if (eventCountMap[boxId]) {
          // Update hour count.
          if (eventCountMap[boxId][hour]) {
            eventCountMap[boxId][hour]++;
          } else {
            eventCountMap[boxId][hour] = 1;
          }
        } else {
          eventCountMap[boxId] = { [hour]: 1 }; // Create new object to keep track of hour count.
        }
        // });
      });

      // Create dataset
      // eslint-disable-next-line max-len
      const colors = ['rgb(167,197,189)', 'rgb(229,221,203)', 'rgb(235,123,89)', 'rgb(207,70,71)', 'rgb(82,70,86)', 'rgb(0,214,144)'];
      const chartDatasets = [];
      Object.keys(eventCountMap).forEach(deviceId => {
        const randomColorIndex = Math.floor(Math.random() * (((colors.length - 1) - 0) + 0));
        const randomColor = colors.splice(randomColorIndex, 1); // Remove selected color from array.
        const dataset = {};
        dataset.label = `Device ${deviceId}`;
        // dataset.backgroundColor = Random.choice(colors);
        dataset.backgroundColor = randomColor.pop(); // Only 1 elem in spliced array, so we pop it.
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
          datasets: chartDatasets,
        },
        options: {
          scales: {
            xAxes: [{
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: 'Hour of Day',
              },
            }],
            yAxes: [{
              ticks: {
                beginAtZero: true,
              },
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: 'Event Count',
              },
            }],
          },
        },
      });
    }
  });
});
