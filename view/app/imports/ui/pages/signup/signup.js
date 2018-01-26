import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { Accounts } from 'meteor/accounts-base';
import { FlowRouter } from 'meteor/kadira:flow-router';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import { setUserRole } from '../../../api/users/UsersCollectionMethods';
import './signup.html';
import '../../components/form-controls/text-form-control.html';

Template.signup.onCreated(function signupOnCreated() {
  const template = this;

  // Define form error message. These should probably be defined elsewhere, as they are general use case messages.
  SimpleSchema.messages({
    passwordMismatch: 'Passwords do not match one another',
  });

  // Define signup form schema so we can validate input.
  template.signupFormSchema = new SimpleSchema({
    firstName: { type: String },
    lastName: { type: String },
    email: {
      type: String,
      regEx: SimpleSchema.RegEx.Email,
    },
    password: {
      type: String,
    },
    confirmPassword: {
      type: String,
      custom: function () { // eslint-disable-line consistent-return
        if (this.value !== this.field('password').value) {
          return 'passwordMismatch';
        }
      },
    },
  });

  template.validationContext = template.signupFormSchema.namedContext('Signup_Page');
  template.formSubmissionErrors = new ReactiveVar();
});

Template.signup.events({
  'submit .signup-form': function (event) {
    event.preventDefault();
    const template = Template.instance();

    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;
    const confirmPassword = event.target.confirmPassword.value;

    const formData = { firstName, lastName, email, password, confirmPassword };

    // Clear old validation errors, clean data, and re-validate.
    template.validationContext.resetValidation();
    template.signupFormSchema.clean(formData);
    template.validationContext.validate(formData);

    // Continue upon validation success.
    if (template.validationContext.isValid()) {
      Accounts.createUser({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
      }, (error, result) => { // eslint-disable-line no-unused-vars
        if (error) {
          template.formSubmissionErrors.set(error);
        } else {
          // User created successfully and is automatically logged in at this point.
          const loggedInUserID = Meteor.userId();
          // Now set user role.
          setUserRole.call({ userID: loggedInUserID, role: 'user' });
          FlowRouter.go('/'); // Redirect to home page.
        }
      });
    }
  },
});
