import { Meteor } from 'meteor/meteor';
import { UserProfiles } from '../../api/users/UserProfilesCollection';
import { ROLE } from '../../api/opq/Role';


function initAdminUser() {
  if (!Meteor.isTest && !Meteor.isAppTest) {
    if (!Meteor.settings.adminUser) {
    console.log('Error: adminUser not specified in view.config.settings.');
    } else {
      const username = Meteor.settings.adminUser.username;
      const firstName = Meteor.settings.adminUser.firstName;
      const lastName = Meteor.settings.adminUser.lastName;
      const password = Meteor.settings.adminUser.password;
      if ((username === 'changeme') || (password === 'changeme')) {
        console.log('Error: You must change the admin username and password in view.config.settings.');
      } else
        if (!UserProfiles.hasAdminUser()) {
          console.log(`Defining admin user: ${username}`);
          UserProfiles.define({ username, firstName, lastName, password, role: ROLE.ADMIN });
        }
    }
  }
}

/**
 * Define the test user at startup if we are in test mode.
 */
Meteor.startup(() => {
  initAdminUser();
});
