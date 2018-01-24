import { Template } from 'meteor/templating';

// Templates and Sub-Template Inclusions
import './research.html';
import '../../components/liveMeasurements/liveMeasurements.js';
import '../../components/eventCountChart/eventCountChart.js';
import '../../components/filterForm/filterForm.js';
import '../../components/eventList/eventList.js';


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
});

Template.research.helpers({

});

Template.research.events({

});
