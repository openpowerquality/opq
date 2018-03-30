import { BoxEvents } from '../../api/box-events/BoxEventsCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { Events } from '../../api/events/EventsCollection';
import { Trends } from '../../api/trends/TrendsCollection.js';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { Measurements } from '../../api/measurements/MeasurementsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

BoxEvents.publish();
BoxOwners.publish();
Events.publish();
Measurements.publish();
OpqBoxes.publish();
SystemStats.publish();
Trends.publish();
UserProfiles.publish();
