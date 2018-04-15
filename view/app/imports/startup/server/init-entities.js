import { Meteor } from 'meteor/meteor';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../api/locations/LocationsCollection';
import { Regions } from '../../api/regions/RegionsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

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

/**
 * Define entities at system startup.  Locations must be defined before regions and opqBoxes.
 */
Meteor.startup(() => {
  initEntity('locations', Locations);
  initEntity('regions', Regions);
  initEntity('opqBoxes', OpqBoxes);
  initEntity('userProfiles', UserProfiles);
});
