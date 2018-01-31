import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { Accounts } from 'meteor/accounts-base';
import { ReactiveVar } from 'meteor/reactive-var';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import _ from 'lodash';
import { FlowRouter } from 'meteor/kadira:flow-router';
import { getCurrentUserProfile, updateUser, updateEmail } from '../../../api/users/UsersCollectionMethods';
import '../../components/form-controls/text-form-control.html';
import '../../components/form-controls/hidden-field.html';
import './userAdmin.html';

Template.User_Admin_Page.onCreated(function () {
  const template = this;

  // Redirect to login page if not signed in. Login page should have signup button.
  template.autorun(() => {
    const currentLoggedInUserId = Meteor.userId();
    if (!currentLoggedInUserId) {
      // Without setTimeout, the url in the browser itself won't change (even though the template itself does change)
      Meteor.setTimeout(() => {
        FlowRouter.go('/signup');
      }, 1);
    }
  });

  template.currentUserProfile = new ReactiveVar();
  template.currentPerson = new ReactiveVar();
  template.formSucesssMessage = new ReactiveVar();

  // Define form error message. These should probably be defined elsewhere, as they are general use case messages.
  SimpleSchema.messages({
    passwordMismatch: 'Passwords do not match one another',
  });

  // Define user update form schema so we can validate input.
  template.userUpdateFormSchema = new SimpleSchema({
    userID: { type: String },
    firstName: { type: String },
    lastName: { type: String },
    email: {
      type: String,
      regEx: SimpleSchema.RegEx.Email,
    },
    password: {
      type: String,
      optional: true,
    },
    newPassword: {
      type: String,
      optional: true,
    },
    confirmNewPassword: {
      type: String,
      optional: true,
      custom: function () { // eslint-disable-line consistent-return
        if (this.value !== this.field('newPassword').value) {
          return 'passwordMismatch';
        }
      },
    },
  });

  template.validationContext = template.userUpdateFormSchema.namedContext('User_Admin_Page');
  template.formSubmissionErrors = new ReactiveVar();

  // Get current User.
  template.autorun(() => {
    template.currentUser = Meteor.user();

    getCurrentUserProfile.call({}, (err, userProfile) => {
      if (err) {
        console.log(err); // eslint-disable-line no-console
        // Redirect to login/signup page if not logged in or other problem occurs.
        // if (!template.currentUser) {
        //   FlowRouter.go('/signup');
        // }
      } else {
        template.currentUserProfile.set(userProfile);
      }
    });
  });
});

Template.User_Admin_Page.onRendered(function () {

});

Template.User_Admin_Page.helpers({
  userData() {
    const template = Template.instance();
    const userProfile = template.currentUserProfile.get();
    // const person = template.currentPerson.get();
    return userProfile;
  },
  userDataField(fieldName) {
    const template = Template.instance();
    const userProfile = template.currentUserProfile.get();
    if (userProfile) {
      return userProfile[fieldName];
    }
    return null;
  },
  getFormSuccessMessage() {
    const message = Template.instance().formSucesssMessage.get();
    return message;
  },
});

Template.User_Admin_Page.events({
  'submit #userForm': function (event) {
    event.preventDefault();
    const template = Template.instance();
    console.log(template.validationContext); // eslint-disable-line no-console

    const userID = event.target.userID.value;
    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;
    const newPassword = event.target.newPassword.value;
    const confirmNewPassword = event.target.confirmNewPassword.value;

    const formData = { userID, firstName, lastName, email, password, newPassword, confirmNewPassword };

    // Clear old validation errors, clean data, and re-validate.
    template.validationContext.resetValidation();
    template.formSubmissionErrors.set(null);
    template.userUpdateFormSchema.clean(formData);
    template.validationContext.validate(formData);

    // Continue upon validation success.
    if (template.validationContext.isValid()) {
      // Change email if needed.
      if (formData.email) {
        // eslint-disable-next-line no-unused-vars
        updateEmail.call({ userID: formData.userID, newEmail: formData.email }, (error, oldEmail) => {
          if (error) {
            console.log(error); // eslint-disable-line no-console
            template.formSubmissionErrors.set(error);
          } else {
            template.formSucesssMessage.set('Settings updated!');
          }
        });
      }

      // Change password if needed.
      if (formData.password && formData.newPassword && formData.confirmNewPassword
          && (formData.newPassword === formData.confirmNewPassword)) {
        // eslint-disable-next-line no-unused-vars
        Accounts.changePassword(formData.password, formData.newPassword, (error, result) => {
          if (error) {
            console.log(error); // eslint-disable-line no-console
            template.formSubmissionErrors.set(error);
          } else {
            template.formSucesssMessage.set('Settings updated!');
          }
        });
      }

      // Update User
      const userObj = _.pick(formData, 'firstName', 'lastName');
      updateUser.call({ userID: formData.userID, userObj }, (error, result) => { // eslint-disable-line no-unused-vars
        if (error) {
          console.log(error); // eslint-disable-line no-console
          template.formSubmissionErrors.set(error);
        } else {
          template.formSucesssMessage.set('Settings updated!');
        }
      });
    }
  },
});
