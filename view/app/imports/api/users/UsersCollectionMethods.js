import { Meteor } from 'meteor/meteor';
import { Accounts } from 'meteor/accounts-base';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Roles } from 'meteor/alanning:roles';
import { Users } from './UsersCollection';

export const totalUsersCount = new ValidatedMethod({
  name: 'Users.totalUsersCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return Users.find({}).count();
  },
});

export const createUser = new ValidatedMethod({
  name: 'Users.createUser',
  validate: new SimpleSchema({
    firstName: { type: String },
    lastName: { type: String },
    email: {
      type: String,
      regEx: SimpleSchema.RegEx.Email,
    },
    password: {
      type: String,
    },
  }).validator({ clean: true }),
  run({ firstName, lastName, email, password }) {
    if (!this.isSimulation) {
      // Note, we can't use Users.define() currently because we need to use Accounts.createUser() to create the
      // new user because it properly uses bcrypt to hash the password from the client.
      // Once we refactor OPQView to not allow users to create their own accounts, we can then use Users.define()
      // to create users (because we will be creating a random password for them on the server - there is no client
      // side communication to worry about).
      return Users.define({ email, password, first_name: firstName, last_name: lastName });
    }
    return null;
  },
});

export const setUserRole = new ValidatedMethod({
  name: 'Users.setUserRole',
  validate: new SimpleSchema({
    userID: { type: String },
    role: { type: String },
  }).validator({ clean: true }),
  run({ userID, role }) {
    if (!this.isSimulation) {
      // Get currently logged in user.
      const currentLoggedInUserID = this.userId;
      if (!currentLoggedInUserID) throw new Meteor.Error('Users.getCurrentUser.notLoggedIn', 'User not logged in.');
      if (userID !== currentLoggedInUserID) throw new Meteor.Error('Users.getCurrentUser.userMismatch', 'Invalid User');

      // Only allow 'user' role for now. Admins should be set manually.
      if (role !== 'user') throw new Meteor.Error('Users.setUserRole', 'Only allowed to set role as "user"');

      // Set role.
      // We are using group-based roles; 'opq-view' is the default group used for general-purpose app permissions.
      Roles.addUsersToRoles(userID, [role], 'opq-view');
    }
    return null;
  },
});

export const getCurrentUserProfile = new ValidatedMethod({
  name: 'Users.getCurrentUserProfile',
  validate: new SimpleSchema({}).validator({ clean: true }),
  run() {
    if (!this.isSimulation) {
      // Get currently logged in user.
      const userId = this.userId;
      if (!userId) {
        throw new Meteor.Error('Users.getCurrentUser', 'User not logged in.');
      }
      const user = Users.findOne({ _id: userId });
      const profile = {
        _id: user._id,
        first_name: user.first_name,
        last_name: user.last_name,
        boxes: user.boxes,
        email: user.emails[0].address,
        roles: user.roles,
      };
      return profile;
    }
    return null;
  },
});

export const updateUser = new ValidatedMethod({
  name: 'Users.updateUser',
  validate: new SimpleSchema({
    userID: { type: String },
    userObj: { type: Object },
    'userObj.firstName': { type: String },
    'userObj.lastName': { type: String },
  }).validator({ clean: true }),
  run({ userID, userObj }) {
    if (!this.isSimulation) {
      const currentLoggedInUserID = this.userId;

      if (!currentLoggedInUserID) throw new Meteor.Error('Users.updateUser.notLoggedIn', 'User not logged in.');
      // eslint-disable-next-line max-len
      if (userID !== currentLoggedInUserID) throw new Meteor.Error('Users.updateUser.userMismatch', 'Unauthorized user.');

      return Users.updateUser(userID, {
        first_name: userObj.firstName,
        last_name: userObj.lastName,
      });
    }
    return null;
  },
});

export const updateEmail = new ValidatedMethod({
  name: 'Users.updateEmail',
  validate: new SimpleSchema({
    userID: { type: String },
    newEmail: { type: String },
  }).validator({ clean: true }),
  run({ userID, newEmail }) {
    if (!this.isSimulation) {
      const currentLoggedInUser = Meteor.user();
      if (!currentLoggedInUser) throw new Meteor.Error('Users.updateEmail.notLoggedIn', 'User not logged in.');

      const currentUserID = currentLoggedInUser._id;
      if (currentUserID !== userID) throw new Meteor.Error('Users.updateEmail.userMismatch', 'Unauthorized user.');

      const currentEmail = currentLoggedInUser.emails[0].address;
      // Meteor does not provide a changeEmail function, so we instead have to separately use the addEmail and
      // removeEmail functions to get the job done.
      // First we need to check if the new email is taken already.
      const existingUser = Accounts.findUserByEmail(newEmail);
      if (existingUser && existingUser._id !== currentUserID) {
        throw new Meteor.Error('Users.updateEmail.emailUnavailable', 'That e-mail address is already in use.');
      }

      if (!existingUser) {
        // Note, these functions do not take a callback for some reason.
        Accounts.addEmail(currentUserID, newEmail);
        Accounts.removeEmail(currentUserID, currentEmail);
        return currentEmail; // Return old email address.
      }
    }
    return null;
  },
});
