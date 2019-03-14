import { Meteor } from 'meteor/meteor';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../api/locations/LocationsCollection';
import { Regions } from '../../api/regions/RegionsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';
import { testUsername, testUserPassword } from '../../api/test/test-utilities';
import { ROLE } from '../../api/opq/Role';

/**
 * Generic function used to load definitions from the settings.*.json file.
 * @param name The field in the settings file containing the entity definitions.
 * @param collection The collection whose define method will be called on each definition.
 */
function initEntity(name, collection) {
  const definitions = Meteor.settings.initialEntities[name] || [];
  console.log(`Initializing ${definitions.length} ${name}`);
  definitions.map(definition => collection.define(definition));
}

/**
 * Initialize entities in order. Note that Locations must be defined before Regions and OpqBoxes.
 */
function initAllEntities() {
  initEntity('locations', Locations);
  initEntity('regions', Regions);
  initEntity('opqBoxes', OpqBoxes);
  initEntity('userProfiles', UserProfiles);
}

function defineTestUser() {
  if (Meteor.isAppTest) {
    console.log(`Defining test user: ${testUsername}`);
    UserProfiles.define({ username: testUsername, firstName: 'Test', lastName: 'User', password: testUserPassword,
    role: ROLE.ADMIN });
  }
}

/**
 * Define entities at system startup.
 * Set initialEntities to true in the settings file to initialize Locations, Regions etc. if none are defined.
 * To initialize entities even when they already exist in the DB, then you must set an environment variable when
 * running Meteor like this:
 * <code>
 *   $ VIEW_FORCE_INIT_ENTITIES=true meteor npm run start
 * </code>
 * This helps ensure that the DB is re-initialized only when you really want it to be re-initialized and that
 * inadvertant commits of enabled=true doesn't propagate into the production DB.
 */
Meteor.startup(() => {
  if (Meteor.settings.initialEntities && Meteor.settings.initialEntities.enabled) {
    if (process.env.VIEW_FORCE_INIT_ENTITIES) {
      initAllEntities();
    } else
      if ((Locations.count() === 0) && (OpqBoxes.count() === 0)) {
        initAllEntities();
      }
  }
});

/**
 * Define the test user at startup if we are in test mode.
 */
Meteor.startup(() => {
  defineTestUser();
});
