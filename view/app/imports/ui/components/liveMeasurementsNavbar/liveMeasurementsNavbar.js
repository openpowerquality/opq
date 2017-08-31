import './liveMeasurementsNavbar.html';
import { Measurements } from '../../../api/measurement/MeasurementCollection.js';
import { getActiveDeviceIdsVM } from '../../../api/measurement/MeasurementCollectionMethods.js';
import { jQueryPromise } from '../../../utils/utils.js';

import '../liveMeasurements/liveMeasurements.js';

Template.liveMeasurementsNavbar.onCreated(function liveMeasurementsNavbarOnCreated() {
  const template = this;

  template.selectedDeviceId = new ReactiveVar();
  template.activeDeviceIds = new ReactiveVar();
  template.measurementStartTimeSecondsAgo = new ReactiveVar(60);

  template.showPopup = new ReactiveVar(false);



  // // Validate data context.
  // template.autorun(() => {
  //
  //   new SimpleSchema({
  //     flashAlertReactiveVar: {type: ReactiveVar},
  //     withMarginTop: {type: Boolean, optional: true}
  //   }).validate(Template.currentData());
  // });


  // Check for active devices, handles initial/default device selection.
  template.autorun(function() {
    const selectedDeviceId = template.selectedDeviceId.get();

    if (template.subscriptionsReady()) {
      getActiveDeviceIdsVM.call({
        startTimeMs: Date.now() - (60 * 1000)
      }, (err, deviceIds) => {
        if (err) console.log(err);
        if (deviceIds && deviceIds.length > 0) {
          template.activeDeviceIds.set(deviceIds);
          if (!selectedDeviceId) template.selectedDeviceId.set(deviceIds[0]); // Select first device by default.
        }
      });
    }
  });

  // Subscription
  template.autorun(function() {
    const selectedDeviceId = template.selectedDeviceId.get();
    const secondsAgo = template.measurementStartTimeSecondsAgo.get();

    if (secondsAgo && selectedDeviceId) {
      Measurements.subscribe(Measurements.publicationNames.RECENT_MEASUREMENTS, template, secondsAgo, selectedDeviceId);
    }
  });

  // // Ensures selected device is highlighted.
  // template.autorun(function() {
  //   const selectedDeviceId = template.selectedDeviceId.get();
  //
  //   if (selectedDeviceId && template.subscriptionsReady()) {
  //     // Un-highlight old device, highlight new device.
  //     jQueryPromise('#deviceSelection button.active', 200, 2000)
  //         .then(deviceBtn => deviceBtn.removeClass('active'))
  //         .catch(error => console.log(error));
  //
  //     jQueryPromise(`#device-${selectedDeviceId}`, 200, 2000)
  //         .then(deviceBtn => deviceBtn.addClass('active'))
  //         .catch(error => console.log(error));
  //   }
  // });

  // Handles graph plotting.
  template.autorun(function() {
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
      const measurements = Measurements.find({device_id: selectedDeviceId}, {sort: {timestamp_ms: 1}})
          .fetch()
          .filter(measurement => measurement.timestamp_ms >= startTime);

      if (measurements.length > 0) {
        const voltages = measurements.map(data => {
          return [data.timestamp_ms - timeZoneOffset, data.voltage];
        });

        const frequencies = measurements.map(data => {
          return [data.timestamp_ms - timeZoneOffset, data.frequency];
        });

        $.plot('#voltagePlotNavbar', [voltages], {
          xaxis: {
            show: false,
            mode: 'time'
          },
          yaxis: {
            show: false
          }
        });

        $.plot('#freqPlotNavbar', [frequencies], {
          xaxis: {
            show: false,
            mode: 'time'
          },
          yaxis: {
            show: false
          }
        });
      }
    }
  });

  // template.autorun(function() {
  //   const showPopup = template.showPopup.get();
  //
  //   if (showPopup && template.subscriptionsReady()) {
  //
  //   }
  // });
});

Template.liveMeasurementsNavbar.onRendered(function() {
  const template = this;
  // const mrs = jQueryPromise('#measurementsNavbar', 100, 1000);
  //
  // mrs.then(target => target.popup({
  //   popup : template.$('#measurementsPopup'),
  //   hoverable: true,
  //   position: 'bottom left'
  // }));

  // Meteor.setTimeout(function() {
  //   console.log(template.$('#measurementsNavbar'));
  //   console.log(template.$('#measurementsPopup'));
  //   console.log('hi');
  //
  //   template.$('#measurementsNavbar').popup({
  //     popup : template.$('#measurementsPopup'),
  //     hoverable: true,
  //     position: 'bottom left'
  //   });
  // }, 3000);

  template.$('#measurementsNavbar').popup({
    popup : template.$('#measurementsPopup'),
    hoverable: true,
    position: 'bottom left',
    distanceAway: 5,
    onShow: function() {
      template.showPopup.set(true);
      console.log('showing');
    },
    onHide: function() {
      template.showPopup.set(false);
      console.log('hiding');
    }
  });

 // template.autorun(function() {
 //   //if (template.subscriptionsReady()) {
 //     Tracker.afterFlush(function() {
 //       console.log('hi');
 //       console.log(template.$('#measurementsNavbar'));
 //       // template.$('#measurementsNavbar').popup({
 //       //   popup : template.$('#measurementsPopup'),
 //       //   hoverable: true,
 //       //   position: 'bottom left'
 //       // });
 //     });
 //   //}
 // });

});

Template.liveMeasurementsNavbar.helpers({
  newestMeasurement() {
    const template = Template.instance();
    const selectedDeviceId = template.selectedDeviceId.get();

    if (selectedDeviceId && template.subscriptionsReady()) {
      const measurement = Measurements.findOne({device_id: selectedDeviceId}, {sort: {timestamp_ms: -1}});
      return measurement;
    }
  },
  showPopup() {
    const template = Template.instance();
    const showPopup = template.showPopup.get();

    return showPopup;
  }
});

// Template.liveMeasurementsNavbar.events({
//   'mouseenter #measurementsNavbar': function(event) {
//     console.log(event.target.id);
//     if (event.target.id == 'measurementsNavbar') {
//       Template.instance().showPopup.set(true);
//     }
//   },
//   'mouseleave #measurementsNavbar': function(event) {
//     if (event.target.id == 'measurementsNavbar' ) {
//       Template.instance().showPopup.set(false);
//     }
//   }
// });


