import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import Chartjs from 'chart.js';
import Moment from 'moment';
import { dataContextValidator, jQueryPromise } from '../../../utils/utils.js';
import { ReactiveVarHelper } from '../../../modules/ReactiveVarHelper';
import { monthlyBoxTrends, getMostRecentTrendMonth } from '../../../api/trends/TrendsCollectionMethods';

// Templates and Sub-Template Inclusions
import './monthlyTrends.html';


Template.monthlyTrends.onCreated(function () {
  const template = this;

  dataContextValidator(template, new SimpleSchema({
    filtersRV: { type: ReactiveVarHelper },
  }), null);

  template.trendsChart = null; // Chartjs instance
  template.currentTrend = new ReactiveVar();
  template.currentBoxID = new ReactiveVar();
  template.currentMonthYear = new ReactiveVar(); // {month, year}
  template.dailyTrends = new ReactiveVar();
  template.monthlyTrends = new ReactiveVar();
  template.isLoadingMonthlyTrends = new ReactiveVar(false);

  template.data.filtersRV.onChange(newFilters => {
    if (newFilters.monthPicker) {
      const selectedDate = Moment(newFilters.monthPicker);
      const month = selectedDate.month();
      const year = selectedDate.year();
      template.currentMonthYear.set({ month, year });
    }
    if (newFilters.opqBoxPicker) {
      template.currentBoxID.set(newFilters.opqBoxPicker);
    }
    if (newFilters.trendPicker) {
      template.currentTrend.set(newFilters.trendPicker);
    }
  });

  // Set the default boxID and monthYear (from the most recent Trend document). Also default currentTrend
  getMostRecentTrendMonth.call({}, (error, { box_id, month, year }) => {
    if (error) {
      console.log(error);
    } else {
      template.data.filtersRV.set({
        monthPicker: Moment().month(month).year(year).valueOf(),
        opqBoxPicker: box_id,
        trendPicker: 'uptime',
      });
      template.currentBoxID.set(box_id);
      template.currentMonthYear.set({ month, year });
      template.currentTrend.set('uptime');
    }
  });

  // Retrieve new monthly trends data whenever selected boxID or MonthYear changes.
  template.autorun(() => {
    const currentMonthYear = template.currentMonthYear.get();
    const currentBoxID = template.currentBoxID.get();
    if (currentMonthYear && currentBoxID) {
      template.isLoadingMonthlyTrends.set(true);
      // eslint-disable-next-line max-len
      monthlyBoxTrends.call({ box_id: currentBoxID, month: currentMonthYear.month, year: currentMonthYear.year }, (error, { dailyTrends, monthlyTrends }) => {
        template.isLoadingMonthlyTrends.set(false);
        if (error) {
          console.log(error);
        } else {
          // console.log(dailyTrends);
          // console.log(monthlyTrends);
          template.dailyTrends.set(dailyTrends);
          template.monthlyTrends.set(monthlyTrends);
        }
      });
    }
  });
});

Template.monthlyTrends.onRendered(function () {
  const template = this;

  template.autorun(() => {
    const currentBoxID = template.currentBoxID.get();
    const monthlyTrends = template.monthlyTrends.get();
    const dailyTrends = template.dailyTrends.get();
    const currentMonthYear = template.currentMonthYear.get();
    const currentTrend = template.currentTrend.get();
    const isLoadingMonthlyTrends = template.isLoadingMonthlyTrends.get();

    if (currentBoxID && currentTrend && monthlyTrends && dailyTrends && currentMonthYear
        && !isLoadingMonthlyTrends && template.subscriptionsReady()) {
      const month = currentMonthYear.month;
      const year = currentMonthYear.year;
      const startOfMonth = Moment().month(month).year(year).startOf('month')
          .valueOf();

      // Calculate labels.
      const daysInCurrentMonth = Moment(startOfMonth).daysInMonth();
      const days = [];
      for (let i = 1; i < daysInCurrentMonth + 1; i++) {
        days.push(i);
      }

      // Create Dataset.
      const chartDatasets = [];
      const dataset = {};
      let yAxisLabel = ''; // Shouldn't do it this way using the same switch statement, but will fix later;
      let chartTitle = '';
      dataset.label = `OPQBox ID: ${currentBoxID}`;
      dataset.backgroundColor = 'rgba(0, 203, 255, 0.4)';
      dataset.data = days.map(day => {
        let data = null;
        const dayTrend = dailyTrends[day];
        switch (currentTrend) {
          case 'uptime':
            data = dayTrend.uptime;
            chartTitle = 'Uptime';
            yAxisLabel = 'Uptime Percentage';
            break;
          case 'voltageMin':
            data = (dayTrend.voltage) ? dayTrend.voltage.min : 0;
            chartTitle = 'Min Voltage';
            yAxisLabel = 'Voltage';
            break;
          case 'voltageMax':
            data = (dayTrend.voltage) ? dayTrend.voltage.max : 0;
            chartTitle = 'Max Voltage';
            yAxisLabel = 'Voltage';
            break;
          case 'voltageAverage':
            data = (dayTrend.voltage) ? dayTrend.voltage.average : 0;
            chartTitle = 'Average Voltage';
            yAxisLabel = 'Voltage';
            break;
          case 'frequencyMin':
            data = (dayTrend.frequency) ? dayTrend.frequency.min : 0;
            chartTitle = 'Min Frequency';
            yAxisLabel = 'Frequency';
            break;
          case 'frequencyMax':
            data = (dayTrend.frequency) ? dayTrend.frequency.max : 0;
            chartTitle = 'Max Frequency';
            yAxisLabel = 'Frequency';
            break;
          case 'frequencyAverage':
            data = (dayTrend.frequency) ? dayTrend.frequency.average : 0;
            chartTitle = 'Average Frequency';
            yAxisLabel = 'Frequency';
            break;
          case 'thdMin':
            data = (dayTrend.thd) ? dayTrend.thd.min : 0;
            chartTitle = 'Min THD';
            yAxisLabel = 'THD';
            break;
          case 'thdMax':
            data = (dayTrend.thd) ? dayTrend.thd.max : 0;
            chartTitle = 'Max THD';
            yAxisLabel = 'THD';
            break;
          case 'thdAverage':
            data = (dayTrend.thd) ? dayTrend.thd.average : 0;
            chartTitle = 'Average THD';
            yAxisLabel = 'THD';
            break;
          default:
            break;
        }

        return data;
      });
      chartDatasets.push(dataset);

      // Create chart
      const chartOptions = {
        type: 'line',
        data: {
          labels: days,
          datasets: chartDatasets,
        },
        options: {
          scales: {
            xAxes: [{
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: 'Day of Month',
              },
            }],
            yAxes: [{
              ticks: {
                beginAtZero: true,
              },
              stacked: true,
              scaleLabel: {
                display: true,
                labelString: yAxisLabel,
              },
            }],
          },
          title: {
            display: true,
            text: chartTitle,
          },
        },
      };

      // Need this to ensure the trendsChart canvas is rendered before attemping to create the chart. Normally this
      // wouldn't be necessary, but the isLoading Spinner if/else block has a template re-rendering delay and this
      // autorun sometimes finishes before the canvas element is rendered on page, causing an error.
      jQueryPromise('#trendsChart', 100, 2000, template)
        .then(trendsChartCtx => {
          if (template.trendsChart) template.trendsChart.destroy();
          template.trendsChart = new Chartjs(trendsChartCtx, chartOptions);
        })
        .catch(error => console.log(error));
    }
  });
});

Template.monthlyTrends.helpers({
  getMonthlyTrends() {
    const monthlyTrends = Template.instance().monthlyTrends.get();
    return monthlyTrends;
  },
  isLoadingMonthlyTrends() {
    return Template.instance().isLoadingMonthlyTrends.get();
  },
});
