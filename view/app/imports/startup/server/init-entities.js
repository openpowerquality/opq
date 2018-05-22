import { Meteor } from 'meteor/meteor';
import { Accounts } from 'meteor/accounts-base';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../api/locations/LocationsCollection';
import { Regions } from '../../api/regions/RegionsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';
import { testUsername, testUserPassword } from '../../api/test/test-utilities';

/**
 * Generic function used to load definitions from the settings.*.json file.
 * @param name The field in the settings file containing the entity definitions.
 * @param collection The collection whose define method will be called on each definition.
 */
function initEntity(name, collection) {
  const definitions = Meteor.settings[name] || [];
  console.log(`Initializing ${definitions.length} ${name}`);
  definitions.map(definition => collection.define(definition));
}

function defineTestUser() {
  if (Meteor.isAppTest) {
    console.log(`Defining test user: ${testUsername}`);
    Accounts.createUser({ username: testUsername, email: testUsername, password: testUserPassword });
  }
}

/**
 * Define entities at system startup.  Locations must be defined before regions and opqBoxes.
 */
Meteor.startup(() => {
  if (Meteor.settings.initializeEntities) {
    initEntity('locations', Locations);
    initEntity('regions', Regions);
    initEntity('opqBoxes', OpqBoxes);
    initEntity('userProfiles', UserProfiles);
  }
});

/**
 * Define the test user at startup if we are in test mode.
 */
Meteor.startup(() => {
  defineTestUser();
});
