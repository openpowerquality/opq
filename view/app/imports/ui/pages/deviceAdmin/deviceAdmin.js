import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { ReactiveVar } from 'meteor/reactive-var';
import { Accounts } from 'meteor/accounts-base';
import { FlowRouter } from 'meteor/kadira:flow-router';
import _ from 'lodash';
import { getCurrentPerson, updatePerson, updateEmail } from '../../../api/person/PersonCollectionMethods.js';
import { userAdminPageSchema } from '../../../utils/schemas';
import '../../components/form-controls/text-form-control.html';
import '../../components/form-controls/hidden-field.html';
import './deviceAdmin.html';

Template.deviceAdmin.onCreated(function () {
  const template = this;
  template.currentUser; // eslint-disable-line no-unused-expressions
  template.currentPerson = new ReactiveVar();

  template.validationContext = userAdminPageSchema.namedContext('UserAdmin_Page');
  template.formSubmissionErrors = new ReactiveVar();


  // Get current User and Person.
  template.autorun(() => {
    template.currentUser = Meteor.user();

    getCurrentPerson.call({}, (err, person) => {
      if (err) {
        console.log(err); // eslint-disable-line no-console
        // Redirect to login/signup page if not logged in or other problem occurs.
        if (!template.currentUser) {
          FlowRouter.go('/signup');
        }
      } else {
        template.currentPerson.set(person);
        console.log('currUser: ', template.currentUser); // eslint-disable-line no-console
        console.log('currPerson: ', person); // eslint-disable-line no-console
      }
    });
  });
});

Template.deviceAdmin.onRendered(function () {
  // const template = this;

});

Template.deviceAdmin.helpers({
  userData() {
    const template = Template.instance();
    const user = template.currentUser;
    const person = template.currentPerson.get();

    if (user && person) {
      const userData = {
        email: user.emails[0].address,
        firstName: person.firstName,
        lastName: person.lastName,
      };

      console.log('userData: ', userData);
      return userData;
    }
    return null;
  },
  userDataField(fieldName) {
    const template = Template.instance();
    const user = template.currentUser;
    const person = template.currentPerson.get();

    if (user && person) {
      const userData = {
        email: user.emails[0].address,
        firstName: person.firstName,
        lastName: person.lastName,
        userId: person.userId,
      };

      return userData[fieldName];
    }
    return null;
  },
});

Template.deviceAdmin.events({
  'submit #userForm': function (event) {
    /* eslint-disable no-console */
    event.preventDefault();
    const template = Template.instance();
    console.log(template.validationContext);

    const userId = event.target.userId.value;
    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;
    const newPassword = event.target.newPassword.value;
    const confirmNewPassword = event.target.confirmNewPassword.value;

    const formData = { userId, firstName, lastName, email, password, newPassword, confirmNewPassword };
    console.log(formData);

    // Clear old validation errors, clean data, and re-validate.
    template.validationContext.resetValidation();
    template.formSubmissionErrors.set(null);
    userAdminPageSchema.clean(formData);
    template.validationContext.validate(formData);
    console.log('cleaned: ', formData);
    console.log('ValidationContext isValid? ', template.validationContext.isValid());

    // Continue upon validation success.
    if (template.validationContext.isValid()) {
      // Change email if needed.
      if (formData.email) {
        updateEmail.call({ userId, newEmail: email }, (error, result) => { // eslint-disable-line no-unused-vars
          if (error) {
            console.log(error);
            template.formSubmissionErrors.set(error);
          } else {
            console.log('E-mail updated.');
          }
        });
      }

      // Change password if needed.
      if (formData.password && formData.newPassword && formData.confirmNewPassword
          && (formData.newPassword === formData.confirmNewPassword)) {
        // eslint-disable-next-line no-unused-vars
        Accounts.changePassword(formData.password, formData.newPassword, (error, result) => {
          if (error) {
            console.log(error);
            template.formSubmissionErrors.set(error);
          } else {
            // Set success message.
            console.log('Password changed');
          }
        });
      }

      // Update Person
      const personObj = _.pick(formData, 'firstName', 'lastName', 'userId');
      updatePerson.call(personObj, (error, result) => { // eslint-disable-line no-unused-vars
        if (error) {
          console.log(error);
          template.formSubmissionErrors.set(error);
        } else {
          console.log('User settings updated.');
        }
      });
    }
    /* eslint-enable no-console */
  },
});
