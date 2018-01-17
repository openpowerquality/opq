import { Template } from 'meteor/templating';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import Moment from 'moment';
// import { EventMetaData } from '../../../api/events/EventsCollection.js';
import { Events } from '../../../api/events/EventsCollection';
import { dataContextValidator } from '../../../utils/utils.js';
import { filterFormSchema } from '../../../utils/schemas.js';


// Template inclusions.
import './eventList.html';

Template.eventList.onCreated(function () {
  const template = this;

  // Validate data context.
  dataContextValidator(template, new SimpleSchema({
    filters: { type: filterFormSchema, optional: true }, // Optional because data context not available immediately.
    selectedEventRV: { type: ReactiveVar },
  }), null);

  template.currentStartTime = new ReactiveVar();
  template.currentEndTime = new ReactiveVar();
  template.selectedEvent = template.data.selectedEventRV;

  // Set ReactiveVars when receiving new filter data.
  template.autorun(() => {
    const dataContext = Template.currentData();
    if (dataContext && dataContext.filters) {
      if (dataContext.filters.startTime) template.currentStartTime.set(Moment(dataContext.filters.startTime).valueOf());
      if (dataContext.filters.endTime) template.currentEndTime.set(Moment(dataContext.filters.endTime).valueOf());
    }
  });

  // Subscribe to event meta data for the given time range.
  template.autorun(() => {
    const startTime = template.currentStartTime.get();
    const endTime = template.currentEndTime.get();
    if (startTime || endTime) {
      template.subscribe(Events.publicationNames.GET_EVENT_META_DATA, { startTime, endTime });
    }
  });
});

Template.eventList.onRendered(function () {

});

Template.eventList.helpers({
  events() {
    const template = Template.instance();
    const startTime = template.currentStartTime.get();
    const endTime = template.currentEndTime.get();
    if ((startTime || endTime) && template.subscriptionsReady()) {
      const eventsSelector = Events.queryConstructors().getEventMetaData({ startTime, endTime });
      const events = Events.find(eventsSelector, { sort: { event_start: -1 } });
      return events;
    }
    return null;
  },
});

Template.eventList.events({
  // 'click #event-list tr td a': function(event, template) {
  //   event.preventDefault();
  //   const route = FlowRouter.path('eventDetailsRoute');
  //   console.log(route);
  //   // FlowRouter.go(Flow)
  // },
  // 'click #event-list tr': function(event, template) {
  //   event.preventDefault();
  //   const tr = event.currentTarget;
  //   const selEvent_id = new Mongo.ObjectID(tr.id);
  //   template.selectedEvent.set(selEvent_id);
  //   template.$('#event-list > tbody > tr').removeClass('active');
  //   template.$(`#event-list tr#${selEvent_id}`).addClass('active');
  // }
});
