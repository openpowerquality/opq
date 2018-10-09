import { Email } from 'meteor/email';
import SimpleSchema from 'simpl-schema';
import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';

export const sendTestEmail = new ValidatedMethod({
  name: 'email.testEmail',
  validate: new SimpleSchema({
    recipients: { type: Array },
    'recipients.$': { type: String },
  }).validator({ clean: true }),
  run({ recipients }) {
    if (Meteor.isServer) {
      Email.send({
        to: recipients,
        from: 'Open Power Quality <postmaster@mail.openpowerquality.org>',
        subject: 'Messaging Test',
        text: 'This is a test.',
      });
    }
  },
});
