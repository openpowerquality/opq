import { Measurements } from '../../api/measurements/MeasurementsCollection.js';
import { Events } from '../../api/events/EventsCollection';
import { BoxEvents } from '../../api/box-events/BoxEventsCollection.js';
import { Trends } from '../../api/trends/TrendsCollection.js';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';


Measurements.publish();
Events.publish();
BoxEvents.publish();
Trends.publish();
SystemStats.publish();
OpqBoxes.publish();
