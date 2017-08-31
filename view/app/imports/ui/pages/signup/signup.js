import { Template } from 'meteor/templating';
import { Accounts } from 'meteor/accounts-base'
import { FlowRouter } from 'meteor/kadira:flow-router';
import { ReactiveVar } from 'meteor/reactive-var';
import './signup.html';
import '../../components/form-controls/text-form-control.html';
import { signupPageSchema } from '../../../utils/schemas.js';
import { createPerson } from '../../../api/persons/personsMethods.js';

Template.signup.onCreated(function signupOnCreated() {
  const template = this;

  template.validationContext = signupPageSchema.namedContext('Signup_Page');
  template.formSubmissionErrors = new ReactiveVar();

});



Template.signup.events({
  'submit .signup-form': function(event) {
    event.preventDefault();
    const template = Template.instance();
    console.log(template.validationContext);

    const firstName = event.target.firstName.value;
    const lastName = event.target.lastName.value;
    const email = event.target.email.value;
    const password = event.target.password.value;
    const confirmPassword = event.target.confirmPassword.value;

    const formData = {firstName, lastName, email, password, confirmPassword};
    // console.log(formData);

    // Clear old validation errors, clean data, and re-validate.
    template.validationContext.resetValidation();
    signupPageSchema.clean(formData);
    template.validationContext.validate(formData);
    // console.log('ValidationContext isValid? ', template.validationContext.isValid());

    // Continue upon validation success.
    if (template.validationContext.isValid()) {
      // Create User, then Person in subsequent callback.
      Accounts.createUser({email: email, password: password}, function(error) {
        if (error) {
          console.log(error);
          template.formSubmissionErrors.set(error.reason);
          // template.validationContext.addInvalidKeys()
        } else {
          // User created successfully and is automatically logged in.
          const currUserId = Meteor.userId();

          // Create Person obj with userId reference, then call createPerson method.
          const person = {
            userId: currUserId,
            firstName: firstName,
            lastName: lastName
          };

          createPerson.call(person, (error, person_id) => {
            if (error) {
              console.log(error);
            } else {
              console.log("Inserted Person successfully: " + person_id);
              FlowRouter.go("/"); // Redirect to home page.
            }
          });

        }
      });
    }

  }
});
