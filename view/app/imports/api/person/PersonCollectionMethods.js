import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Roles } from 'meteor/alanning:roles';
import { Accounts } from 'meteor/accounts-base';
import { Persons } from './PersonCollection.js';


export const createPerson = new ValidatedMethod({
  name: 'Persons.createPerson',
  validate: Persons.getSchema().validator({clean: true}),
  run(person) {
    // Make sure userId exists before inserting.
    if (!Meteor.users.findOne({_id: person.userId})) {
      throw new Meteor.Error('personsMethods.createPerson.noUser' ,'User Id does not exist.');
    }

    // Set default User role. (perhaps better to do this using Accounts.onCreateUser?)
    Roles.addUsersToRoles(person.userId, 'user', 'user-type');

    return Persons.define(person); // Document id is returned on success.
  }
});

export const getCurrentPerson = new ValidatedMethod({
  name: 'Persons.getCurrentPerson',
  validate: null,
  run() {
    // Get currently logged in user.
    const userId = this.userId;
    if (!userId) {
      throw new Meteor.Error('Persons.getCurrentPerson.notLoggedIn', 'User not logged in.');
    }
    const person = Persons.findOne({userId}, {});
    return person;
  }
});

export const updatePerson = new ValidatedMethod({
  name: 'Persons.updatePerson',
  validate: Persons.getSchema().validator({clean: true}),
  run(person) {
    const userId = this.userId;

    if (!userId) throw new Meteor.Error('Persons.updatePerson.notLoggedIn', 'User not logged in.');
    if (userId !== person.userId) throw new Meteor.Error('Persons.updatePerson.userMismatch', 'Unauthorized user.');

    return Persons.update({userId}, {$set: person});
  }
});

export const updateEmail = new ValidatedMethod({
  name: 'Persons.updateEmail',
  validate: new SimpleSchema({
    userId: {type: String},
    newEmail: {type: String}
  }).validator({clean: true}),
  run({userId, newEmail}) {
    if (!this.isSimulation) {
      const currentUser = Meteor.user();
      const currentUserId = currentUser._id;
      const currentEmail = currentUser.emails[0].address;

      if (!currentUserId) throw new Meteor.Error('Persons.updateEmail.notLoggedIn', 'User not logged in.');
      if (currentUserId !== userId) throw new Meteor.Error('Persons.updateEmail.userMismatch', 'Unauthorized user.');

      // Meteor does not provide a changeEmail function, so we instead have to separately use the addEmail and
      // removeEmail functions to get the job done.
      // First we need to check if the new email is taken already.
      const existingUser = Accounts.findUserByEmail(newEmail);
      if (existingUser && existingUser._id != currentUserId) {
        throw new Meteor.Error('Persons.updateEmail.emailUnavailable', 'That e-mail address is already in use.');
      }

      if (!existingUser) {
        // Note, these functions do not take a callback for some reason.
        Accounts.addEmail(currentUserId, newEmail);
        Accounts.removeEmail(currentUserId, currentEmail);
      }
    }
  }
});

Meteor.methods({
  updatePerson(personModifier) {
    // Validate against schema. No need to check the $unset portion, because we're simply removing it.
    check(personModifier.$set, Persons.simpleSchema());

    if (!Persons.findOne({_id: personModifier.id})) {
      throw new Meteor.Error('persons.updatePerson.noPerson', 'Person does not exist.');
    }

    return Persons.update(
        {_id: personModifier.id},
        {
          $set: personModifier.$set,
          $unset: personModifier.$unset
        }
    );
  },
  // addDeviceToPerson(user_id, device_id) {
  //   check(user_id, String);
  //   check(device_id, String);
  //
  //   const userId = this.userId;
  //   if (userId !== user_id) throw new Meteor.Error('persons.addDeviceToPerson.userMismatch', 'Logged in user does not match user invoking method call.');
  //
  //   const device = OpqDevices.findOne({_id: new Mongo.ObjectID(device_id)});
  //   if (!device) throw new Meteor.Error('persons.addDeviceToPerson.invalidDevice', 'Device does not exist.');
  //
  //   const person = Persons.findOne({userId: userId});
  //   if (person) {
  //     // Push deviceId to Person, and push personId to Device.
  //     const personResult = Persons.update({_id: person._id}, {$push: {opqDevices: device._id}});
  //     const deviceResult = OpqDevices.update({_id: device._id}, {$push: {persons: person._id}});
  //
  //     return 'Device successfully linked.';
  //     if (personResult === 1 && deviceResult === 1) {
  //       return 'Device successfully linked!';
  //     }
  //   }
  //
  //   return 'Unable to link device.';
  // }
});

export const getPersonIdByUserId = (userId) => {
  return Persons.findOne({userId: userId})._id;
};
