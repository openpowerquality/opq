import { FlowRouter } from 'meteor/kadira:flow-router';
import { BlazeLayout } from 'meteor/kadira:blaze-layout';
import '../../ui/layouts/appLayout/appLayoutPublic.js';
import '../../ui/pages/signup/signup.js';
import '../../ui/pages/research/research.js';
import '../../ui/pages/eventDetails/eventDetails.js';
// import '../../ui/pages/userAdmin/userAdmin.js';
// import '../../ui/pages/deviceAdmin/deviceAdmin.js';


FlowRouter.route('/signup', {
  name: 'signupRoute',
  action: function () {
    BlazeLayout.render('appLayoutPublic', {
      main: 'signup',
    });
  },
});

FlowRouter.route('/', {
  name: 'researchRoute',
  action: function () {
    BlazeLayout.render('appLayoutPublic', {
      main: 'research',
    });
  },
});
//
// // Redirect to accounts page by default.
// FlowRouter.route('/settings', {
//   name: 'settingsRoute',
//   action: function () {
//     FlowRouter.go('/settings/account');
//   },
// });
//
// FlowRouter.route('/settings/account', {
//   name: 'accountRoute',
//   action: function () {
//     BlazeLayout.render('appLayoutPublic', {
//       main: 'userAdmin',
//     });
//   },
// });
//
// FlowRouter.route('/settings/devices', {
//   name: 'devicesRoute',
//   action: function () {
//     BlazeLayout.render('appLayoutPublic', {
//       main: 'deviceAdmin',
//     });
//   },
// });
//
FlowRouter.route('/event/:event_id', {
  name: 'eventDetailsRoute',
  action: function () {
    BlazeLayout.render('appLayoutPublic', {
      main: 'Event_Details_Page',
    });
  },
});

