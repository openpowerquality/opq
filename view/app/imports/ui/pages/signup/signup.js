import { Meteor } from 'meteor/meteor';
import { Template } from 'meteor/templating';
import { Accounts } from 'meteor/accounts-base';
import { FlowRouter } from 'meteor/kadira:flow-router';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import { createUser } from '../../../api/users/UsersCollectionMethods';
import './signup.html';
import '../../components/form-controls/text-form-control.html';
// import { signupPageSchema } from '../../../utils/schemas.js';
// import { createPerson } from '../../../api/person/PersonCollectionMethods.js';

Template.signup.onCreated(function signupOnCreated() {
  const template = this;

  // Define signup form schema so we can validate input. (This should be elsewhere).
  SimpleSchema.messages({
    passwordMismatch: 'Passwords do not match one another',
  });

  template.signupFormSchema = new SimpleSchema({
    firstName: { type: String },
    lastName: { type: String },
    email: { // Accounts-password
      type: String,
      label: 'E-mail *',
      regEx: SimpleSchema.RegEx.Email,
    },
    password: { // Accounts-password
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
  // template.validationContext = signupPageSchema.namedContext('Signup_Page');
  template.formSubmissionErrors = new ReactiveVar();
});

Template.signup.events({
  'submit .signup-form': function (event) {
    event.preventDefault();
    const template = Template.instance();
    // console.log(template.validationContext);

    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;
    const confirmPassword = event.target.confirmPassword.value;

    const formData = { firstName, lastName, email, password, confirmPassword };
    // console.log(formData);

    // Clear old validation errors, clean data, and re-validate.
    template.validationContext.resetValidation();
    template.signupFormSchema.clean(formData);
    // signupPageSchema.clean(formData);
    template.validationContext.validate(formData);
    console.log('ValidationContext isValid? ', template.validationContext.isValid());

    // Continue upon validation success.
    if (template.validationContext.isValid()) {
      createUser.call({ firstName, lastName, email, password }, (error, newUserID) => {
        if (error) {
          console.log(error); // eslint-disable-line no-console
          template.formSubmissionErrors.set(error);
        } else {
          console.log(`User created successfully: ${newUserID}`); // eslint-disable-line no-console
          FlowRouter.go('/'); // Redirect to home page.
        }
      });
      // Create User, then Person in subsequent callback.
      // Accounts.createUser({ email: email, password: password }, function (error) {
      //   if (error) {
      //     console.log(error); // eslint-disable-line no-console
      //     template.formSubmissionErrors.set(error.reason);
      //     // template.validationContext.addInvalidKeys()
      //   } else {
      //     // User created successfully and is automatically logged in.
      //     const currUserId = Meteor.userId();
      //
      //     // Create Person obj with userId reference, then call createPerson method.
      //     const person = {
      //       userId: currUserId,
      //       firstName: firstName,
      //       lastName: lastName,
      //     };
      //
      //     createPerson.call(person, (error, personId) => { // eslint-disable-line no-shadow
      //       if (error) {
      //         console.log(error); // eslint-disable-line no-console
      //       } else {
      //         console.log(`Inserted Person successfully: ${personId}`); // eslint-disable-line no-console
      //         FlowRouter.go('/'); // Redirect to home page.
      //       }
      //     });
      //   }
      // });
    }
  },
});
