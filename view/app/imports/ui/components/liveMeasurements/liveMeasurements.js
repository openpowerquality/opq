import { Template } from 'meteor/templating';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import { Measurements } from '../../../api/measurements/MeasurementsCollection.js';
import { jQueryPromise, dataContextValidator } from '../../../utils/utils.js';

// Templates
import './liveMeasurements.html';

Template.liveMeasurements.onCreated(function liveMeasurementsOnCreated() {
  const template = this;

  // Validate data context
  dataContextValidator(template, new SimpleSchema({
    selectedDeviceIdReactiveVar: { type: ReactiveVar, optional: true },
    opqBoxID: { type: String },
  }));

  template.selectedDeviceId = (template.data.selectedDeviceIdReactiveVar)
      ? template.data.selectedDeviceIdReactiveVar
      : new ReactiveVar(template.data.opqBoxID);

  template.activeDeviceIds = new ReactiveVar();
  template.measurementStartTimeSecondsAgo = new ReactiveVar(60);

  // Retrieve list of active device ids (active within last minute). Selects initial device for monitoring.
  // template.autorun(function () {
  //   const selectedDeviceId = template.selectedDeviceId.get();
  //
  //   if (template.subscriptionsReady()) {
  //     getActiveBoxIds.call({
  //       startTimeMs: Date.now() - (60 * 1000),
  //     }, (err, deviceIds) => {
  //       if (err) console.log(err);
  //       if (deviceIds && deviceIds.length > 0) {
  //         template.activeDeviceIds.set(deviceIds);
  //         if (!selectedDeviceId) template.selectedDeviceId.set(deviceIds[0]); // Select first device by default.
  //       }
  //     });
  //   }
  // });

  // Subscription
  template.autorun(function () {
    const selectedDeviceId = template.selectedDeviceId.get();
    const secondsAgo = template.measurementStartTimeSecondsAgo.get();

    if (secondsAgo && selectedDeviceId) {
      console.log('subscribe measurements: ', secondsAgo, selectedDeviceId);
      Measurements.subscribe(Measurements.publicationNames.RECENT_MEASUREMENTS, template, secondsAgo, selectedDeviceId);
    }
  });
});

Template.liveMeasurements.onRendered(function () {
  const template = this;

  // Highlights the 1-minute button on the live device monitor.
  if (template.subscriptionsReady()) {
    jQueryPromise('#1m', 100, 2000, template)
        .then(button => button.addClass('active'))
        .catch(error => console.log(error));
  }

  // Ensures selected device is highlighted.
  template.autorun(function () {
    const selectedDeviceId = template.selectedDeviceId.get();

    if (selectedDeviceId && template.subscriptionsReady()) {
      // Un-highlight old device, highlight new device.
      jQueryPromise('#deviceSelection button.active', 100, 2000, template)
          .then(deviceBtn => deviceBtn.removeClass('active'))
          .catch(error => console.log(error));

      jQueryPromise(`#device-${selectedDeviceId}`, 100, 2000, template)
          .then(deviceBtn => deviceBtn.addClass('active'))
          .catch(error => console.log(error));
    }
  });

  // Handles graph plotting.
  template.autorun(function () {
    const selectedDeviceId = template.selectedDeviceId.get();
    const measurementStartTimeSecondsAgo = template.measurementStartTimeSecondsAgo.get();
    const timeZoneOffset = new Date().getTimezoneOffset() * 60 * 1000; // Positive if -UTC, negative if +UTC.

    if (selectedDeviceId && template.subscriptionsReady()) {
      // Note on the filter: Although the publication is supposed to send removal calls to the client on measurements
      // outside of the startTime range, it seems that once in a while these messages get lost over the wire.
      // Consequently, the server believes the measurement has been removed, while the client collection still holds it,
      // resulting in the plot displaying data outside of the intended time range (which gets worse over time).
      // The simple solution is to filter on the client side and ensure we are only displaying data within the intended
      // time frame.
      // Also of note: It's much faster to simply filter() on the resulting mongo query result, rather than to query
      // with {timestamp_ms: {$gte: startTime}}. Meteor's Minimongo implementation isn't very efficient.
      const startTime = Date.now() - (measurementStartTimeSecondsAgo * 1000);
      const measurements = Measurements.find({ box_id: selectedDeviceId }, { sort: { timestamp_ms: 1 } })
          .fetch()
          .filter(measurement => measurement.timestamp_ms >= startTime);

      if (measurements.length > 0) {
        const voltages = measurements.map(data => [data.timestamp_ms - timeZoneOffset, data.voltage]);

        const frequencies = measurements.map(data => [data.timestamp_ms - timeZoneOffset, data.frequency]);

        // Calculate tick size for graph.
        // const tickSize = template.measurementStartTimeSecondsAgo.get() / 5;
        const measurementsTimestampRange = voltages[voltages.length - 1][0] - voltages[0][0];
        const tickSize = measurementsTimestampRange / (5 * 1000);

        // jQueryPromise('[id^=miniVoltagePlot]', 100, 200, template)
        //     .then(voltagePlotDiv => console.log(voltagePlotDiv.attr('id'), 'FROM PROMISE'))
        //     .catch(error => console.log(error));
        const voltagePlotId = template.$('[id^=miniVoltagePlot]').attr('id');
        const freqPlotId = template.$('[id^=miniFreqPlot]').attr('id');

        $.plot(`#${voltagePlotId}`, [voltages], { // eslint-disable-line no-undef
          xaxis: {
            mode: 'time',
            timeformat: '%H:%M:%S',
            tickSize: [tickSize, 'second'],
          },
          yaxis: {
            tickDecimals: 2,
          },
        });

        $.plot(`#${freqPlotId}`, [frequencies], { // eslint-disable-line no-undef
          xaxis: {
            mode: 'time',
            timeformat: '%H:%M:%S',
            tickSize: [tickSize, 'second'],
          },
          yaxis: {
            tickDecimals: 3,
          },
        });
      }
    }
  });
});

Template.liveMeasurements.helpers({
  measurements() {
    const template = Template.instance();
    const selectedDeviceId = template.selectedDeviceId.get();

    if (selectedDeviceId && template.subscriptionsReady()) {
      const measurements = Measurements.find(
          { box_id: selectedDeviceId },
          { sort: { timestamp_ms: -1 }, limit: 10 },
      );
      return measurements;
    }
    return null;
  },
  newestMeasurement() {
    const template = Template.instance();
    const selectedDeviceId = template.selectedDeviceId.get();

    if (selectedDeviceId && template.subscriptionsReady()) {
      const measurement = Measurements.findOne({ box_id: selectedDeviceId }, { sort: { timestamp_ms: -1 } });
      return measurement;
    }
    return null;
  },
  deviceIds() {
    const template = Template.instance();
    const activeDeviceIds = template.activeDeviceIds.get();

    return (activeDeviceIds && activeDeviceIds.length > 0) ? activeDeviceIds : null;
  },
  deviceStatus() {
    const template = Template.instance();
    const activeDeviceIds = template.activeDeviceIds.get();
    // return (activeDeviceIds && activeDeviceIds.length > 0) ? 'Device Online' : 'Device Offline';
    return (activeDeviceIds && activeDeviceIds.length > 0) ? null : 'Device Offline';
  },
});

Template.liveMeasurements.events({
  /* eslint-disable no-unused-vars */
  'click #1m': function (event) {
    const template = Template.instance();
    template.$('#1m').addClass('active');
    template.$('#5m').removeClass('active');
    template.$('#10m').removeClass('active');
    template.measurementStartTimeSecondsAgo.set(60);
  },
  'click #5m': function (event) {
    const template = Template.instance();
    template.$('#5m').addClass('active');
    template.$('#1m').removeClass('active');
    template.$('#10m').removeClass('active');
    template.measurementStartTimeSecondsAgo.set(60 * 5);
  },
  'click #10m': function (event) {
    const template = Template.instance();
    template.$('#10m').addClass('active');
    template.$('#1m').removeClass('active');
    template.$('#5m').removeClass('active');
    template.measurementStartTimeSecondsAgo.set(60 * 10);
  },
  'click #deviceSelection button': function (event) {
    const template = Template.instance();
    const deviceId = Number(event.currentTarget.id.replace('device-', ''));
    // $('#deviceSelection > button.active').removeClass('active');
    // $(`#device-${deviceId}`).addClass('active');
    template.selectedDeviceId.set(deviceId);
  },
  /* eslint-enable no-unused-vars */
});

