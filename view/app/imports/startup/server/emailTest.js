import { Email } from 'meteor/email';

/**
 *Test email sending during development
 */

function sendEmail() { // eslint-disable-line
  Email.send({
    to: '8082569623@tmomail.net',
    from: 'postmaster@mail.openpowerquality.org',
    subject: 'Email test',
    text: 'text',
  });
}

// Meteor.startup(() => {
//   sendEmail();
// });
