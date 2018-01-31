import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import flatpickr from 'flatpickr';
import { mapify } from 'es6-mapify';
import Moment from 'moment';
import { colorQuantify, dataContextValidator, timeUnitString } from '../../../utils/utils.js';
import './filterForm.html';
import '../form-controls/text-form-control.html';
import '../form-controls/select-form-control.js';
import '../../../../node_modules/flatpickr/dist/flatpickr.min.css';
import { eventsCountMap, getMostRecentEvent } from '../../../api/events/EventsCollectionMethods.js';
import { getBoxIDs } from '../../../api/opq-boxes/OpqBoxesCollectionMethods';
import { ReactiveVarHelper } from '../../../modules/ReactiveVarHelper';

// Schema this form uses to validate submission.
export const filterFormSchema = new SimpleSchema({
  minFrequency: { type: Number, optional: true },
  maxFrequency: { type: Number, optional: true },
  minVoltage: { type: Number, optional: true },
  maxVoltage: { type: Number, optional: true },
  minDuration: { type: Number, optional: true },
  maxDuration: { type: Number, optional: true },
  startTime: { type: Number, optional: true },
  endTime: { type: Number, optional: true },
  dayPicker: { type: Number, optional: true },
  monthPicker: { type: Number, optional: true },
  opqBoxPicker: { type: String, optional: true },
  trendPicker: { type: String, optional: true },
});

Template.Filter_Form.onCreated(function () {
  const template = this;
  const dataContext = template.data;

  // Validate data context.
  dataContextValidator(template, new SimpleSchema({
    frequencyRange: { type: Boolean, optional: true },
    voltageRange: { type: Boolean, optional: true },
    durationRange: { type: Boolean, optional: true },
    itic: { type: Boolean, optional: true },
    timeInterval: { type: Boolean, optional: true },
    dayPicker: { type: Boolean, optional: true },
    monthPicker: { type: Boolean, optional: true },
    opqBoxPicker: { type: Boolean, optional: true },
    trendPicker: { type: Boolean, optional: true },
    filtersRV: { type: ReactiveVarHelper },
  }));

  // Attach filtersRV data context to template.
  template.filtersRV = template.data.filtersRV;

  // Keep track of selected opq box for OpqBoxPicker
  if (dataContext.opqBoxPicker) {
    template.selectedOpqBox = new ReactiveVar();
  }
  // Keep track of selected trend for TrendPicker
  if (dataContext.trendPicker) {
    template.selectedTrend = new ReactiveVar();
  }

  // Check for default values, if any.
  template.autorun(() => {
    const filters = template.filtersRV.get();
    if (filters) {
      if (filters.opqBoxPicker && !template.defaultOpqBoxPicker) {
        template.defaultOpqBoxPicker = filters.opqBoxPicker;
        template.selectedOpqBox.set(template.defaultOpqBoxPicker);
      }
      if (filters.trendPicker) {
        template.selectedTrend.set(filters.trendPicker);
      }
    }
  });


  // List of all OpqBox IDs for the OpqBoxPicker selection options.
  template.opqBoxIDs = new ReactiveVar();

  // Form Validation Context
  template.validationContext = filterFormSchema.namedContext('Filter_Form');

  template.defaultDate = new ReactiveVar();

  // Holds the timestamp of the beginning of month. Initial value is the current month.
  template.dayPickerCurrentMonth = new ReactiveVar(Moment().startOf('month').valueOf());

  // Holds most recent event count map/dict.
  template.currentEventsCountMap = new ReactiveVar();

  if (dataContext.dayPicker || dataContext.timeInterval) {
    // When month changes, retrieve event count for that month. This data will be inserted to dayPicker widget.
    template.autorun(() => {
      const currentMonth = template.dayPickerCurrentMonth.get();
      if (currentMonth) {
        const endOfMonth = Moment(currentMonth).endOf('month').valueOf();
        eventsCountMap.call({
          timeUnit: 'dayOfMonth',
          startTime: currentMonth,
          stopTime: endOfMonth,
        }, (error, eventCountMap) => {
          if (error) {
            console.log(error); // eslint-disable-line no-console
          } else {
            const ecm = mapify(eventCountMap); // Had to be demapified (aka serialized) before being sent from server.
            template.currentEventsCountMap.set(ecm);
          }
        });
      }
    });

    // Find most recent day that had an event.
    getMostRecentEvent.call((error, mostRecentEvent) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        const startOfDay = Moment(mostRecentEvent.target_event_start_timestamp_ms).startOf('day').valueOf();
        template.defaultDate.set(startOfDay);

        // Set default filter form values
        template.filtersRV.set({
          startTime: startOfDay,
          dayPicker: startOfDay,
        });
      }
    });
  }

  if (dataContext.opqBoxPicker) {
    // Get list of all OpqBox IDs for the OpqBoxPicker
    getBoxIDs.call((error, boxIDs) => {
      if (error) {
        console.log(error);
      } else {
        template.opqBoxIDs.set(boxIDs);
      }
    });
  }
});

Template.Filter_Form.onRendered(function () {
  const template = this;
  const dataContext = template.data;

  // MonthPicker flatpickr widget
  if (dataContext.monthPicker) {
    template.autorun(() => {
      const defaultMonthPickerDate = template.filtersRV.get();
      // We only want to initialize the widget once, after we receive a default date.
      if (defaultMonthPickerDate && !template.monthPicker) {
        const defaultDate = defaultMonthPickerDate.monthPicker;
        const onMonthOrYearChange = (dObj, dStr, fp) => {
          // Note: fp.currentMonth is 0-indexed.
          const newMoment = Moment().month(fp.currentMonth).year(fp.currentYear).valueOf();
          fp.setDate(new Date(newMoment));
        };

        const flatpickrConfig = {
          // defaultDate: new Date(Moment().startOf('month').subtract(3, 'months').valueOf()),
          defaultDate: new Date(defaultDate),
          // altInput/format allows us to have a date format inside the text input that is different than what is
          // actually being submitted (which is 'Y-m-d' by default).
          altInput: true,
          altFormat: 'F, Y',
          onYearChange: [onMonthOrYearChange],
          onMonthChange: [onMonthOrYearChange],
          onReady: [
            function (selectedDates, dateStr, instance) {
              instance.innerContainer.style.display = 'none'; // eslint-disable-line no-param-reassign
              instance.monthNav.style.borderRadius = '5px'; // eslint-disable-line no-param-reassign
              instance.monthNav.style.height = '35px'; // eslint-disable-line no-param-reassign
            },
          ],
        };

        template.monthPicker = flatpickr('#monthPicker', flatpickrConfig);
      }
    });
  }

  // DayPicker flatpickr widget.
  // Config here is a bit complicated - but serves as a proof of concept on how to reactively associate data with the
  // flatpickr widget.
  if (dataContext.dayPicker || dataContext.timeInterval) {
    template.autorun(() => {
      const currentMonth = template.dayPickerCurrentMonth.get();
      const eventsCountMap = template.currentEventsCountMap.get(); // eslint-disable-line no-shadow
      const defaultDate = template.defaultDate.get();

      if (defaultDate && currentMonth && eventsCountMap && template.subscriptionsReady()) {
        const flatpickrConfig = {
          onDayCreate: function (dObj, dStr, fp, dayElem) {
            const computation = template.autorun(() => {
              const currDate = dayElem.dateObj;
              const currMonth = Moment(currDate).month(); // 0-11
              const timeUnitKey = timeUnitString(currDate, 'dayOfMonth');

              // Ignore the prevMonthDays and nextMonthDays on calendar.
              if (currMonth === fp.currentMonth) {
                const eventsCountMap2 = template.currentEventsCountMap.get();
                const eventCount = eventsCountMap2.get(timeUnitKey);

                if (eventsCountMap2 && eventCount && template.subscriptionsReady()) {
                  /* eslint-disable no-undef */
                  $(dayElem).attr('data-tooltip', `${eventCount} events`);
                  const bgColor = colorQuantify(eventCount, 1, 250, ['#00ff00', '#ffff00', '#ff0000']);
                  $(dayElem).append(`<span class="flatpickr-day-highlight" style="background: ${bgColor};"></span>`);
                  /* eslint-enable no-undef */
                }
              }
            });

            if (fp.trackerComputations) {
              fp.trackerComputations.push(computation);
            } else {
              fp.trackerComputations = [computation]; // eslint-disable-line no-param-reassign
            }
          },
          onMonthChange: function (selectedDates, dateStr, fpInstance) {
            // Note: It seems this callback is fired AFTER onDayCreate() when we change month.

            // Remove old tracker computations. This is important, otherwise we will end up creating a ton of autoruns.
            const oldComputations = fpInstance.trackerComputations.splice(0, 42);
            oldComputations.forEach(comp => comp.stop());

            // Set RV to new month (which will trigger autorun to method call for new event counts).
            const date = Moment().month(fpInstance.currentMonth)
                .year(fpInstance.currentYear)
                .startOf('month')
                .valueOf();
            template.dayPickerCurrentMonth.set(date);
          },
        };

        // Only instantiate once.
        if (!template.dayPicker) {
          flatpickrConfig.defaultDate = new Date(defaultDate);
          template.dayPicker = flatpickr('#dayPicker', flatpickrConfig);
        }
        if (!template.startTimeFlatpickr) {
          flatpickrConfig.defaultDate = new Date(defaultDate);
          template.startTimeFlatpickr = flatpickr('#startTime', flatpickrConfig);
        }
        if (!template.endTimeFlatpickr) {
          flatpickrConfig.defaultDate = null;
          template.endTimeFlatpickr = flatpickr('#endTime', flatpickrConfig);
        }
      }
    });
  }
});

Template.Filter_Form.helpers({
  opqBoxPickerOptions() {
    const boxIDs = Template.instance().opqBoxIDs.get();
    const defaultOpqBox = Template.instance().defaultOpqBoxPicker;
    if (boxIDs && defaultOpqBox) {
      boxIDs.sort();
      const options = boxIDs.map(id => {
        const option = {
          label: `Box ${id}`,
          value: id,
          isSelected: id === defaultOpqBox,
        };
        return option;
      });
      return options;
    }
    return null;
  },
  selectedOpqBox() {
    const selectedOpqBox = Template.instance().selectedOpqBox.get();
    if (selectedOpqBox) {
      return selectedOpqBox;
    }
    return null;
  },
  trendOptions() {
    const trendTypes = ['uptime', 'voltageMin', 'voltageMax', 'voltageAverage', 'frequencyMin', 'frequencyMax',
      'frequencyAverage', 'thdMin', 'thdMax', 'thdAverage'];

    const defaultTrend = 'uptime';
    const options = trendTypes.map(trend => {
      const option = {
        label: `${trend}`,
        value: trend,
        isSelected: trend === defaultTrend,
      };
      return option;
    });
    return options;
  },
  selectedTrend() {
    const selectedTrend = Template.instance().selectedTrend.get();
    if (selectedTrend) {
      return selectedTrend;
    }
    return null;
  },
});

Template.Filter_Form.events({
  'submit .filter-form'(event, instance) {
    event.preventDefault();
    // const dataContext = instance.data; // Non-reactive

    const formData = {};
    if (event.target.minFrequency) formData.minFrequency = event.target.minFrequency.value;
    if (event.target.maxFrequency) formData.maxFrequency = event.target.maxFrequency.value;

    if (event.target.minVoltage) formData.minVoltage = event.target.minVoltage.value;
    if (event.target.maxVoltage) formData.maxVoltage = event.target.maxVoltage.value;

    if (event.target.minDuration) formData.minDuration = event.target.minDuration.value;
    if (event.target.maxDuration) formData.maxDuration = event.target.maxDuration.value;

    // Flatpickr empty values are empty strings, which would normally be handled by the simple-schema clean function,
    // however, Moment cannot take empty string values, so we much check for a real value before passing to Moment.
    if (event.target.startTime && event.target.startTime.value.length) {
      formData.startTime = Moment(event.target.startTime.value).valueOf();
    }
    if (event.target.endTime && event.target.endTime.value.length) {
      formData.endTime = Moment(event.target.endTime.value).valueOf();
    }
    if (event.target.dayPicker && event.target.dayPicker.value.length) {
      formData.dayPicker = Moment(event.target.dayPicker.value).valueOf();
    }
    if (event.target.monthPicker && event.target.monthPicker.value.length) {
      formData.monthPicker = Moment(event.target.monthPicker.value).valueOf();
    }
    if (event.target.opqBoxPicker) {
      formData.opqBoxPicker = event.target.opqBoxPicker.value;
      console.log(formData.opqBoxPicker);
    }
    if (event.target.trendPicker) {
      formData.trendPicker = event.target.trendPicker.value;
      console.log(formData.trendPicker);
    }

    // Clean and validate form data.
    instance.validationContext.resetValidation();
    filterFormSchema.clean(formData);
    instance.validationContext.validate(formData);

    // Set ReactiveVar if valid.
    // if (instance.validationContext.isValid()) instance.filterSource.set(formData);
    if (instance.validationContext.isValid()) instance.filtersRV.set(formData);
  },
});
