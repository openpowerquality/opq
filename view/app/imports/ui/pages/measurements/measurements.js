import { Meteor } from 'meteor/meteor';
import { Mongo } from 'meteor/mongo';
import { Template } from 'meteor/templating';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { ReactiveVar } from 'meteor/reactive-var';
import SimulatedEvents from '../../../api/simulatedEvents/simulatedEvents.js';
import { BoxEvents } from '../../../api/boxEvent/BoxEventCollection.js';
import { getRecentEventDataReqIds } from '../../../api/eventData/EventDataCollectionMethods.js'

// Templates and Sub-Template Inclusions
import './measurements.html';
import '../../components/liveMeasurements/liveMeasurements.js';
import '../../components/map/map.js';
// import '../../components/flashMessage/flashMessage.js';
// import { flashMessageConstructor } from '../../components/flashMessage/flashMessage.js';



Template.measurements.onCreated(function() {
  const template = this;
  //template.flashMessage = new ReactiveVar(createFlashMessageMsgObject('positive', 10, 'Test body message', '', 'feed'));
  // flashMessageConstructor(this);

  template.selectedEventId = new ReactiveVar();
  template.recentEventDataReqIds = new ReactiveVar();
  template.selectedEventDataReqId = new ReactiveVar();

  // Subscriptions
  template.autorun(() => {
    template.subscribe('simulatedEvents', 60);
    //template.subscribe(BoxEvents.publicationNames.COMPLETE_RECENT_BOX_EVENTS, 20);
  });

  // Automatically selects most recent event received from server.
  template.autorun(() => {
    const newestEvent = SimulatedEvents.findOne({}, {sort: {timestamp_ms: -1}});

    if (newestEvent && template.subscriptionsReady()) {
      const newestEventId = newestEvent._id.toHexString();
      template.selectedEventId.set(newestEventId);
    }
  });

  // Ensures most recently selected event is highlighted.
  template.autorun(() => {
    const selectedEventId = template.selectedEventId.get();

    if (selectedEventId && template.subscriptionsReady()) {
      // Highlight newest event, un-highlight old event.
      template.$('#recent-events > tbody >  tr').removeClass('active');
      template.$(`#recent-events tr#${selectedEventId}`).addClass('active');
    }
  });

  // Get most recent EventData Ids.
  template.autorun(() => {
    if (template.subscriptionsReady()) {
      getRecentEventDataReqIds.call({numEvents: 20}, (err, requestIds) => {
        if (err) {
          console.log(err)
        } else {
          console.log(requestIds);
          template.recentEventDataReqIds.set(requestIds);
          template.selectedEventDataReqId.set(requestIds[0]); // Select first event by default.
        }
      });
    }
  });

});

Template.measurements.onRendered(function() {
  const template = this;

  // // Init main-map
  // L.Icon.Default.imagePath = '/packages/bevanhunt_leaflet/images/';
  // template.mainMap = L.map('main-map').setView([21.466700, -157.983300], 10);
  // template.markerLayerGroup = L.layerGroup([]);
  //
  // const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  // const osmAttrib = "Map data © OpenStreetMap contributors";
  // const osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});
  // template.mainMap.addLayer(osm);

  // Plots waveform whenever an event is selected.
  template.autorun(function() {
    const selectedEventId = template.selectedEventId.get();
    const event = SimulatedEvents.findOne({_id: new Mongo.ObjectID(selectedEventId)});
    console.log(event);

    if (selectedEventId && event && template.subscriptionsReady()) {
      Tracker.afterFlush(function() {

        // Plot options. Some of these options are deprecated... fix later.
        const plotOptions = {
          zoom: {
            interactive: true
          },
          pan: {
            interactive: true
          },
          acisLabels: {
            show: true
          },
          xaxis: {
            ticks: 5,
            min: 1000,
            max: 3000
          },
          xaxes: [{
            axisLabel: "Samples"
          }],
          yaxes: [{
            axisLabel: "Voltage"
          }],
          series: {
            lines: {show: true},
            points: {show: false}
          }
        };

        if (event.type == 'Distributed') {
          event.events.forEach(event => {
            const waveformData = event.waveform;

            // Create an array of [x, y] points
            const plotPoints = waveformData.split(",")
                .map(function(pt, idx) {
                  return [idx, parseFloat(pt)];
                });

            // Plot
            $.plot($(`#waveform-${event._id.toHexString()}`), [plotPoints], plotOptions);
          });
        } else {
          const waveformData = event.waveform;

          // Create an array of [x, y] points
          const plotPoints = waveformData.split(",")
              .map(function(pt, idx) {
                return [idx, parseFloat(pt)];
              });

          // Plot
          $.plot($(`#waveform-${selectedEventId}`), [plotPoints], plotOptions);
        }

      });
    }
  });

});

Template.measurements.helpers({
  simEvents() {
    const template = Template.instance();
    const events = SimulatedEvents.find({timestamp_ms: {$gte: Date.now() - 60000}}, {sort: {timestamp_ms: -1}});
    return events;
  },
  selectedEvent() {
    const template = Template.instance();

    const selectedEventId = template.selectedEventId.get();
    const event = SimulatedEvents.findOne({_id: new Mongo.ObjectID(selectedEventId)});

    if (selectedEventId && event && template.subscriptionsReady()) {
      return event;
    }
  },
  formatCoords(coords) {
    console.log(coords);
  },
  getIticBadge: function(itic) {
    let badge;

    switch (itic) {
      case Global.Enums.IticRegion.NO_INTERRUPTION:
        badge = "itic-no-interruption";
        break;
      case Global.Enums.IticRegion.NO_DAMAGE:
        badge = "itic-no-damage";
        break;
      case Global.Enums.IticRegion.PROHIBITED:
        badge = "itic-prohibited";
        break;
      default:
        badge = "N/A";
        break;
    }

    return badge;
  },
  plotMaxWidth: function() {
    const template = Template.instance();
    const width = template.$('#selected-event').width();
    console.log(width);
    return width - 300;
  },
  boxEvents() {
    const boxEvents = BoxEvents.find({}, {sort: {eventEnd: -1}});
    return boxEvents;
  },
  requestIds() {
    const requestIds = Template.instance().recentEventDataReqIds.get();
    return requestIds;
  }
});

Template.measurements.events({
  'click #recent-events tr': function(event) {
    const template = Template.instance();
    console.log(event.currentTarget.id);
    const id = event.currentTarget.id;
    template.selectedEventId.set(id);
  },
  'click td a.coords': function(event) {
    const lat = $(event.currentTarget).attr('lat');
    const lng = $(event.currentTarget).attr('lng');

    L.map('main-map').flyTo([lat, lng], 13);

  }
});