import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import './login.html';

Template.login.onCreated(function() {
  const template = this;

  // Validate data context.
  template.autorun(() => {
    new SimpleSchema({
      withFlashAlert: {type: Object, optional: true},
      "withFlashAlert.message": {type: String},
      "withFlashAlert.type": {type: String},
      "withFlashAlert.expireAtMillis": {type: Number}
    }).validate(Template.currentData());
  });

  // template.flashAlert = (template.data.withFlashAlert) ? new ReactiveVar(template.data.withFlashAlert) : new ReactiveVar();
});

Template.login.helpers({
  loginSchema() {
    return Global.Schemas.Login;
  },
  pathForSignup() {
    return FlowRouter.path('signupRoute');
  }
});

Template.login.events({
  'submit .login-form': function(event) {
    event.preventDefault();

    const email = event.target.email.value;
    const password = event.target.password.value;

    Meteor.loginWithPassword(email, password, function(error) {
      if (error) {
        console.log(error);
      } else {
        console.log('Login successful!: ', email);
      }
    });
  }
});
