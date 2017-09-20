import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import {colorQuantify, dataContextValidator, jQueryPromise, timeUnitString} from '../../../utils/utils.js';
import './filterForm.html';
import '../form-controls/text-form-control.html'
import flatpickr from 'flatpickr';
import '../../../../node_modules/flatpickr/dist/flatpickr.min.css';
import { boxEventsCountMap } from '../../../api/boxEvent/BoxEventCollectionMethods.js';
import { mapify } from 'es6-mapify';
import Moment from 'moment';
import { filterFormSchema } from '../../../utils/schemas.js'

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
  });

  // Form Validation Context
  template.validationContext = filterFormSchema.namedContext('Filter_Form');

  // Holds the timestamp of the beginning of month. Initial value is the current month.
  template.dayPickerCurrentMonth = new ReactiveVar(Moment().startOf('month').toDate());

  // Holds most recent event count map/dict.
  template.currentBoxEventsCountMap = new ReactiveVar();

  // When month changes, retrieve event count for that month. This data will be inserted to dayPicker widget.
  template.autorun(() => {
    const currentMonth = template.dayPickerCurrentMonth.get();
    if (currentMonth) {
      const endOfMonth = Moment(currentMonth).endOf('month').toDate();
      boxEventsCountMap.call({timeUnit: 'dayOfMonth', startTime: currentMonth, stopTime: endOfMonth}, (error, eventCountMap) => {
        if (error) {
          console.log(error)
        } else {
          const ecm = mapify(eventCountMap); // Had to be demapified (aka serialized) before being sent from server.
          template.currentBoxEventsCountMap.set(ecm);
        }
      });
    }
  });

});

Template.Filter_Form.onRendered(function() {
  const template = this;
  const dataContext = template.data;

  // Instantiate flatpickr for startTime and endTime
  if (dataContext.timeInterval) {
    const flatpickrConfig = {
      enableTime: true,
      enableSeconds: true
    };
    template.startTimeFlatpickr = flatpickr('#startTime', flatpickrConfig);
    template.endTimeFlatpickr = flatpickr('#endTime', flatpickrConfig);
  }

  // Instantiate flatpickr widget for dayPicker.
  // Config here is a bit complicated - but serves as a proof of concept on how to reactively associate data with the
  // flatpickr widget.
  if (dataContext.dayPicker) {
    template.autorun(() => {
      const currentMonth = template.dayPickerCurrentMonth.get();
      const eventsCountMap = template.currentBoxEventsCountMap.get();

      if (currentMonth && eventsCountMap && template.subscriptionsReady()) {
        const flatpickrConfig = {
          onDayCreate: function(dObj, dStr, fp, dayElem) {
            const computation = template.autorun(() => {
              const currDate = dayElem.dateObj;
              const currMonth = Moment(currDate).month(); // 0-11
              const timeUnitKey = timeUnitString(currDate, 'dayOfMonth');

              // Ignore the prevMonthDays and nextMonthDays on calendar.
              if (currMonth === fp.currentMonth) {
                const eventsCountMap = template.currentBoxEventsCountMap.get();
                const eventCount = eventsCountMap.get(timeUnitKey);

                if (eventsCountMap && eventCount && template.subscriptionsReady()) {
                  $(dayElem).attr('data-tooltip', `${eventCount} events`);
                  const bgColor = colorQuantify(eventCount, 1, 50, ['#00ff00', '#ffff00', '#ff0000']);
                  $(dayElem).append(`<span class="flatpickr-day-highlight" style="background: ${bgColor};"></span>`);
                }
              }
            });

            (fp.trackerComputations) ? fp.trackerComputations.push(computation) : fp.trackerComputations = [computation];
          },
          onMonthChange: function(selectedDates, dateStr, fpInstance) {
            // Note: It seems this callback is fired AFTER onDayCreate() when we change month.

            // Remove old tracker computations. This is important, otherwise we will end up creating a ton of autoruns.
            const oldComputations = fpInstance.trackerComputations.splice(0,42);
            oldComputations.forEach(comp => comp.stop());

            // Set RV to new month (which will trigger autorun to method call for new event counts).
            const date = Moment().month(fpInstance.currentMonth).year(fpInstance.currentYear).startOf('month').toDate();
            template.dayPickerCurrentMonth.set(date);
          }
        };

        // Only instantiate once.
        if (!template.dayPicker) template.dayPicker = flatpickr('#dayPicker', flatpickrConfig);
      }
    });
  }


});

Template.Filter_Form.events({
  'submit .filter-form'(event, template) {
    event.preventDefault();
    const dataContext = template.data; // Non-reactive

    const formData = {};
    if (event.target.minFrequency) formData.minFrequency = event.target.minFrequency.value;
    if (event.target.maxFrequency) formData.maxFrequency = event.target.maxFrequency.value;

    if (event.target.minVoltage) formData.minVoltage = event.target.minVoltage.value;
    if (event.target.maxVoltage) formData.maxVoltage = event.target.maxVoltage.value;

    if (event.target.minDuration) formData.minDuration = event.target.minDuration.value;
    if (event.target.maxDuration) formData.maxDuration = event.target.maxDuration.value;

    if (event.target.startTime) formData.startTime = event.target.startTime.value;
    if (event.target.endTime) formData.endTime = event.target.endTime.value;

    if (event.target.dayPicker) formData.dayPicker = event.target.dayPicker.value;

    // Clean and validate form data.
    template.validationContext.resetValidation();
    filterFormSchema.clean(formData);
    template.validationContext.validate(formData);

    // Set ReactiveVar if valid.
    if (template.validationContext.isValid()) template.filterSource.set(formData);
  }
});
