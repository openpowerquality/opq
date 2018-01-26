import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import Moment from 'moment';
import { ReactiveVarHelper } from '../../../modules/ReactiveVarHelper';

// Templates and Sub-Template Inclusions
import './research.html';
import '../../components/liveMeasurements/liveMeasurements.js';
import '../../components/eventCountChart/eventCountChart.js';
import '../../components/filterForm/filterForm.js';
import '../../components/eventList/eventList.js';


Template.research.onCreated(function () {
  const template = this;
  template.eventListFilters = new ReactiveVarHelper(template, new ReactiveVar());
  template.eventCountChartFilters = new ReactiveVarHelper(template, new ReactiveVar());
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
});

Template.research.helpers({
  getEventListFiltersRV() {
    return Template.instance().eventListFilters;
  },
  getEventCountChartFiltersRV() {
    return Template.instance().eventCountChartFilters;
  },
  eventListFiltersButtonTimestampString() {
    let outputString = '';
    const eventListFilters = Template.instance().eventListFilters.get();
    if (eventListFilters) {
      const startTime = eventListFilters.startTime;
      const endTime = eventListFilters.endTime;
      outputString = `${Moment(startTime).format('MMM D, YYYY')}`;
      outputString = (endTime)
          ? `${outputString} - ${Moment(endTime).format('MMM D, YYYY')}`
          : `${outputString} - Now`;
    }
    return outputString;
  },
  eventCountChartFiltersButtonTimestampString() {
    let outputString = '';
    const eventCountChartFilters = Template.instance().eventCountChartFilters.get();
    if (eventCountChartFilters) {
      const day = eventCountChartFilters.dayPicker;
      outputString = `${Moment(day).format('MMM D, YYYY')}`;
    }
    return outputString;
  },
});

Template.research.events({

});
