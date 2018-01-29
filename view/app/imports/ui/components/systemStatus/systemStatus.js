import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { totalEventsCount } from '../../../api/events/EventsCollectionMethods';
import { totalBoxEventsCount } from '../../../api/box-events/BoxEventsCollectionMethods';
import { totalOpqBoxesCount, getBoxIDs } from '../../../api/opq-boxes/OpqBoxesCollectionMethods';
import { totalMeasurementsCount, checkBoxStatus } from '../../../api/measurements/MeasurementsCollectionMethods';
import { totalTrendsCount } from '../../../api/trends/TrendsCollectionMethods';
import { totalUsersCount } from '../../../api/users/UsersCollectionMethods';
import { jQueryPromise } from '../../../utils/utils';
import './systemStatus.html';

Template.systemStatus.onCreated(function () {
  const template = this;

  // Collection Counts
  template.totalEvents = new ReactiveVar();
  template.totalBoxEvents = new ReactiveVar();
  template.totalTrends = new ReactiveVar();
  template.totalMeasurements = new ReactiveVar();
  template.totalOpqBoxes = new ReactiveVar();
  template.totalUsers = new ReactiveVar();

  totalEventsCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalEvents.set(count);
    }
  });

  totalBoxEventsCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalBoxEvents.set(count);
    }
  });

  totalOpqBoxesCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalOpqBoxes.set(count);
    }
  });

  totalMeasurementsCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalMeasurements.set(count);
    }
  });

  totalTrendsCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalTrends.set(count);
    }
  });

  totalUsersCount.call((error, count) => {
    if (error) {
      console.log(error); // eslint-disable-line no-console
    } else {
      template.totalUsers.set(count);
    }
  });

  // Check OPQBox Status
  template.opqBoxIDs = new ReactiveVar();
  getBoxIDs.call((error, boxIDs) => {
    if (error) {
      console.log(error);
    } else {
      boxIDs.sort();
      template.opqBoxIDs.set(boxIDs);
    }
  });

  // Live Measurements
  template.showPopup = new ReactiveVar(false);
});

Template.systemStatus.onRendered(function () {
  const template = this;

  template.autorun(() => {
    const opqBoxIDs = template.opqBoxIDs.get();
    if (opqBoxIDs) {
      opqBoxIDs.forEach(boxID => {
        jQueryPromise(`#liveMeasurementsButtonBoxID-${boxID}`, 100, 3000, template)
            .then(button => {
              button.popup({
                popup: template.$(`#liveMeasurementsPopupBoxID-${boxID}`),
                hoverable: true,
                position: 'bottom left',
                distanceAway: 5,
                onShow: function () {
                  template.showPopup.set(true);
                },
                onHide: function () {
                  template.showPopup.set(false);
                },
              });
            });
      });
    }
  });
});

Template.systemStatus.helpers({
  totalEventsCount() {
    return Template.instance().totalEvents.get();
  },
  totalBoxEventsCounts() {
    return Template.instance().totalBoxEvents.get();
  },
  totalOpqBoxesCounts() {
    return Template.instance().totalOpqBoxes.get();
  },
  totalMeasurementsCounts() {
    return Template.instance().totalMeasurements.get();
  },
  totalTrendsCount() {
    return Template.instance().totalTrends.get();
  },
  totalUsersCount() {
    return Template.instance().totalUsers.get();
  },
  opqBoxIDs() {
    return Template.instance().opqBoxIDs.get();
  },
  isBoxActive(boxID) {
    checkBoxStatus.call({ box_id: boxID }, (error, isOnline) => {
      if (error) {
        console.log(error);
      } else {
        console.log(boxID, isOnline);
        return isOnline;
      }
    });
  },
  showPopup() {
    return Template.instance().showPopup.get();
  },
});
