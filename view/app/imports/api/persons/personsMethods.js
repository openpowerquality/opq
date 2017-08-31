import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Roles } from 'meteor/alanning:roles';
import { Persons } from './persons.js';


export const createPerson = new ValidatedMethod({
  name: 'personsMethods.createPerson',
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
