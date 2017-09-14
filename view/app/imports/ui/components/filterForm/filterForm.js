import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import {colorQuantify, dataContextValidator, jQueryPromise} from '../../../utils/utils';
import './filterForm.html';
import '../form-controls/text-form-control.html'
import flatpickr from 'flatpickr';
import '../../../../node_modules/flatpickr/dist/flatpickr.min.css';
import { BoxEvents } from '../../../api/boxEvent/BoxEventCollection';
import Moment from 'moment';

Template.Filter_Form.onCreated(function() {
  const template = this;

  // Validate data context.
  dataContextValidator(template, new SimpleSchema({
    frequencyRange: {type: Boolean, optional: true},
    voltageRange: {type: Boolean, optional: true},
    durationRange: {type: Boolean, optional: true},
    itic: {type: Boolean, optional: true},
    timeInterval: {type: Boolean, optional: true},
    dayPicker: {type: Boolean, optional: true},
    filterSource: {type: ReactiveVar}
  }), null);

  // Attach data context to template.
  template.autorun(() => {
    const dataContext = Template.currentData();
    template.filterSource = (dataContext.filterSource) ? dataContext.filterSource : null;
    console.log('filterSource: ', template.filterSource);

  });

  // Form Validation fields
  //template.validationContext = signupPageSchema.namedContext('Filter_Form');
  //template.formSubmissionErrors = new ReactiveVar();

  // Holds the timestamp of the beginning of month. Initial value is the current month.
  template.dayPickerCurrentMonth = new ReactiveVar(Moment().startOf('month').toDate());

  // Subscription
  template.autorun(() => {
    const currentMonth = template.dayPickerCurrentMonth.get();

    if (currentMonth) {
      const endOfMonth = Moment(currentMonth).endOf('month').toDate();
      console.log('currentMonth: ', currentMonth);
      console.log('endOfMonth: ', endOfMonth);
      template.subscribe(BoxEvents.publicationNames.GET_BOX_EVENTS, {startTime: currentMonth, endTime: endOfMonth});
    }

  });

});

Template.Filter_Form.onRendered(function() {
  const template = this;

  // Instantiate flatpickr widget, attach to template.
  template.autorun(() => {
    const currentMonth = template.dayPickerCurrentMonth.get();

    if (currentMonth && template.subscriptionsReady()) {
      const flatpickrConfig = {
        onDayCreate: function(dObj, dStr, fp, dayElem) {
          const computation = template.autorun(() => {
            const currDate = dayElem.dateObj;
            // Ignore the prevMonthDays and nextMonthDays on calendar.
            if (currDate.getMonth() === fp.currentMonth) {
              const currentMonth = template.dayPickerCurrentMonth.get();
              // console.log('cm new: ', fp.currentMonth, currentMonth, Tracker.currentComputation);

              const endOfDay = Moment(currDate).endOf('day').toDate();
              const selector = BoxEvents.queryConstructors().getBoxEvents({startTime: currDate, endTime: endOfDay});
              const dailyEventsCount = BoxEvents.find(selector, {}).count();

              if (dailyEventsCount && template.subscriptionsReady()) {
                const bgColor = colorQuantify(dailyEventsCount, [1, 50], ['#00ff00', '#ffff00', '#ff0000']);
                $(dayElem).append(`<span class="flatpickr-day-highlight" style="background: ${bgColor};"></span>`);
              }
            }
          });

          (fp.trackerComputations) ? fp.trackerComputations.push(computation) : fp.trackerComputations = [computation];
        },
        onMonthChange: function(selectedDates, dateStr, fpInstance) {
          // Subscribe to month event per day
          console.log('monthChange');
          // $('.flatpickr-day.nextMonthDay span.flatpickr-day-highlight').remove();
          // $('.flatpickr-day.prevMonthDay span.flatpickr-day-highlight').remove();
          const oldComputations = fpInstance.trackerComputations.splice(0,42);
          oldComputations.forEach(comp => comp.stop());
          // console.log('computations: ', fpInstance.trackerComputations);
          // console.log(selectedDates, dateStr, fpInstance);
          // Get the Date obj representing start of the current month.
          const date = Moment().month(fpInstance.currentMonth).year(fpInstance.currentYear).startOf('month').toDate();
          template.dayPickerCurrentMonth.set(date);
        }
      };

      // Only instantiate once.
      if (!template.dayPicker) template.dayPicker = flatpickr('#dayPicker', flatpickrConfig);
    }
  });

});

Template.Filter_Form.events({
  'submit .filter-form'(event, template) {
    event.preventDefault();
    const dataContext = template.data; // Non-reactive

    const formData = {};
    if (dataContext.frequencyRange) {
      formData.minFrequency = event.target.minFrequency.value;
      formData.maxFrequency = event.target.maxFrequency.value;
    }
    if (dataContext.voltageRange) {
      formData.minVoltage = event.target.minVoltage.value;
      formData.maxVoltage = event.target.maxVoltage.value;
    }
    // if (dataContext.durationRange) {
      formData.minDuration = event.target.minDuration.value;
      formData.maxDuration = event.target.maxDuration.value;
    // }
    if (dataContext.timeInterval) {
      formData.startTime = event.target.startTime.value;
      formData.endTime = event.target.endTime.value;
    }

    console.log('Filter_Form formData submit event: ', formData);

    template.filterSource.set(formData);
  }
});
