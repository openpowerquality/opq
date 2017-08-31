import { Measurements } from '../../api/measurement/MeasurementCollection.js';
import { BoxEvents } from '../../api/boxEvent/BoxEventCollection.js';
import { EventData } from '../../api/eventData/EventDataCollection.js';
import '../../api/simulatedEvents/simulatedEventsPublications.js';


Measurements.publish();
BoxEvents.publish();
EventData.publish();