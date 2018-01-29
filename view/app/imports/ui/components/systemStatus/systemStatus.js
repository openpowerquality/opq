import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { totalEventsCount } from '../../../api/events/EventsCollectionMethods';
import { totalBoxEventsCount } from '../../../api/box-events/BoxEventsCollectionMethods';
import { totalOpqBoxesCount, getBoxIDs } from '../../../api/opq-boxes/OpqBoxesCollectionMethods';
import { totalMeasurementsCount, activeBoxIDs } from '../../../api/measurements/MeasurementsCollectionMethods';
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

  template.opqBoxIDs = new ReactiveVar();
  getBoxIDs.call((error, boxIDs) => {
    if (error) {
      console.log(error);
    } else {
      boxIDs.sort();
      template.opqBoxIDs.set(boxIDs);
    }
  });

  // Determine Live OpqBoxes
  template.onlineBoxIDs = new ReactiveVar();
  activeBoxIDs.call((error, onlineIDs) => {
    if (error) {
      console.log(error);
    } else {
      template.onlineBoxIDs.set(onlineIDs);
    }
  });

  // Live Measurements
  template.showPopup1 = new ReactiveVar(false);
  template.showPopup2 = new ReactiveVar(false);
  template.showPopup3 = new ReactiveVar(false);
  template.showPopup4 = new ReactiveVar(false);
  template.showPopup5 = new ReactiveVar(false);
});

Template.systemStatus.onRendered(function () {
  const template = this;

  template.autorun(() => {
    const boxIDs = template.onlineBoxIDs.get();
    if (boxIDs) {
      jQueryPromise('#liveMeasurementsButtonBoxID-1', 200, 10000, template)
          .then(button => {
            button.popup({
              popup: template.$('#liveMeasurementsPopupBoxID-1'),
              hoverable: true,
              position: 'bottom left',
              distanceAway: 5,
              onShow: function () {
                template.showPopup1.set(true);
              },
              onHide: function () {
                template.showPopup1.set(false);
              },
            });
          });

      jQueryPromise('#liveMeasurementsButtonBoxID-2', 200, 10000, template)
          .then(button => {
            button.popup({
              popup: template.$('#liveMeasurementsPopupBoxID-2'),
              hoverable: true,
              position: 'bottom left',
              distanceAway: 5,
              onShow: function () {
                template.showPopup2.set(true);
              },
              onHide: function () {
                template.showPopup2.set(false);
              },
            });
          });

      jQueryPromise('#liveMeasurementsButtonBoxID-3', 200, 10000, template)
          .then(button => {
            button.popup({
              popup: template.$('#liveMeasurementsPopupBoxID-3'),
              hoverable: true,
              position: 'bottom left',
              distanceAway: 5,
              onShow: function () {
                template.showPopup3.set(true);
              },
              onHide: function () {
                template.showPopup3.set(false);
              },
            });
          });

      jQueryPromise('#liveMeasurementsButtonBoxID-4', 200, 10000, template)
          .then(button => {
            button.popup({
              popup: template.$('#liveMeasurementsPopupBoxID-4'),
              hoverable: true,
              position: 'bottom left',
              distanceAway: 5,
              onShow: function () {
                template.showPopup4.set(true);
              },
              onHide: function () {
                template.showPopup4.set(false);
              },
            });
          });

      jQueryPromise('#liveMeasurementsButtonBoxID-5', 200, 10000, template)
          .then(button => {
            button.popup({
              popup: template.$('#liveMeasurementsPopupBoxID-5'),
              hoverable: true,
              position: 'bottom left',
              distanceAway: 5,
              onShow: function () {
                template.showPopup5.set(true);
              },
              onHide: function () {
                template.showPopup5.set(false);
              },
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
    const onlineBoxIDs = Template.instance().onlineBoxIDs.get();
    if (onlineBoxIDs) {
      return !!onlineBoxIDs.find((id) => id === boxID);
    }
    return null;
  },
  showPopup(boxID) {
    return Template.instance()[`showPopup${boxID}`].get();
  },
  showPopup1() {
    return Template.instance().showPopup1.get();
  },
  showPopup2() {
    return Template.instance().showPopup2.get();
  },
  showPopup3() {
    return Template.instance().showPopup3.get();
  },
  showPopup4() {
    return Template.instance().showPopup4.get();
  },
  showPopup5() {
    return Template.instance().showPopup5.get();
  },
});
