import { Meteor } from 'meteor/meteor';
import { UserProfiles } from '../../api/users/UserProfilesCollection';


function initUsers() {
  // Default profiles to an empty array if they are not specified in the settings file.
  const profiles = Meteor.settings.userProfiles || [];
  console.log(`Initializing ${profiles.length} user profiles.`);
  profiles.map(profile => UserProfiles.define(profile));
}

Meteor.startup(() => {
  initUsers();
});
