import { Measurements } from '../../api/measurements/MeasurementsCollection.js';
import { BoxEvents } from '../../api/box-events/BoxEventsCollection.js';


Measurements.publish();
BoxEvents.publish();