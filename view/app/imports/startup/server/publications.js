import { BoxEvents } from '../../api/box-events/BoxEventsCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { Events } from '../../api/events/EventsCollection';
import { Healths } from '../../api/health/HealthsCollection';
import { Locations } from '../../api/locations/LocationsCollection';
import { Trends } from '../../api/trends/TrendsCollection.js';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { Measurements } from '../../api/measurements/MeasurementsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

BoxEvents.publish();
BoxOwners.publish();
Events.publish();
Healths.publish();
Locations.publish();
Measurements.publish();
OpqBoxes.publish();
SystemStats.publish();
Trends.publish();
UserProfiles.publish();

console.log(Measurements.findOne({}, { sort: { timestamp_ms: -1 }}));