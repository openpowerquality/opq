import { Measurements } from '../../api/measurements/MeasurementsCollection.js';
import { Events } from '../../api/events/EventsCollection';
import { BoxEvents } from '../../api/box-events/BoxEventsCollection.js';
import { Trends } from '../../api/trends/TrendsCollection.js';


Measurements.publish();
Events.publish();
BoxEvents.publish();
Trends.publish();
