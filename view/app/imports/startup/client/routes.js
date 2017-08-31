import { FlowRouter } from 'meteor/kadira:flow-router';
import { BlazeLayout } from 'meteor/kadira:blaze-layout';

import '../../ui/layouts/appLayout/appLayoutPublic.js';

import '../../ui/pages/measurements/measurements.js';
import '../../ui/pages/signup/signup.js';
import '../../ui/pages/research/research.js';


FlowRouter.route('/measurements', {
  name: 'liveRoute',
  action: function() {
    BlazeLayout.render('appLayoutPublic', {
      main: 'measurements'
    });
  }
});

FlowRouter.route('/signup', {
  name: 'signupRoute',
  action: function() {
    BlazeLayout.render('appLayoutPublic', {
      main: 'signup'
    });
  }
});

FlowRouter.route('/', {
  name: 'researchRoute',
  action: function() {
    BlazeLayout.render('appLayoutPublic', {
      main: 'research'
    });
  }
});

