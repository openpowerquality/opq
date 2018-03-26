import { BoxEvents } from '../../api/box-events/BoxEventsCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { Events } from '../../api/events/EventsCollection';
import { Measurements } from '../../api/measurements/MeasurementsCollection';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';
import { Trends } from '../../api/trends/TrendsCollection';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

BoxEvents.publish();
BoxOwners.publish();
Events.publish();
Measurements.publish();
OpqBoxes.publish();
SystemStats.publish();
Trends.publish();
UserProfiles.publish();
