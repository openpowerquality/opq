import { Template } from 'meteor/templating';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import Moment from 'moment';
import { Events } from '../../../api/events/EventsCollection';
import { dataContextValidator } from '../../../utils/utils.js';
import { filterFormSchema } from '../../../utils/schemas.js';
import { ReactiveVarHelper } from '../../../modules/ReactiveVarHelper';


// Template inclusions.
import './eventList.html';

Template.eventList.onCreated(function () {
  const template = this;

  // Validate data context.
  dataContextValidator(template, new SimpleSchema({
    filtersRV: { type: ReactiveVarHelper },
  }), null);

  template.currentStartTime = new ReactiveVar();
  template.currentEndTime = new ReactiveVar();

  // Register callback to update current start/end times whenever new time range is set from filter form.
  template.data.filtersRV.onChange(newFilters => {
    template.currentStartTime.set(Moment(newFilters.startTime).valueOf());
    template.currentEndTime.set(Moment(newFilters.endTime).valueOf());
  });

  // Subscribe to all events within the given time range.
  template.autorun(() => {
    const startTime = template.currentStartTime.get();
    const endTime = template.currentEndTime.get();
    if (startTime || endTime) {
      template.subscribe(Events.publicationNames.GET_EVENTS, { startTime, endTime });
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
      const eventsSelector = Events.queryConstructors().getEvents({ startTime, endTime });
      const events = Events.find(eventsSelector, { sort: { target_event_start_timestamp_ms: -1 } });
      return events;
    }
    return null;
  },
});

Template.eventList.events({

});
