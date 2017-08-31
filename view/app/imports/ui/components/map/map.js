import { Meteor } from 'meteor/meteor';
import './map.html';
import SimulatedEvents from '../../../api/simulatedEvents/simulatedEvents.js';

Template.map.onCreated(function mapOnCreated() {
  const template = this;
  // template.mainMap = template.data.mainMap;

  template.autorun(() => {
    Meteor.subscribe('simulatedEvents', 60);
  });

});

Template.map.onRendered(function mapOnRendered() {
  const template = this;

  L.Icon.Default.imagePath = '/packages/bevanhunt_leaflet/images/';
  template.mainMap = L.map('main-map').setView([21.466700, -157.983300], 10);
  template.markerLayerGroup = L.layerGroup([]);

  const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const osmAttrib = "Map data © OpenStreetMap contributors";
  const osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});
  template.mainMap.addLayer(osm);


  template.autorun(() => {
    const event = SimulatedEvents.findOne({}, {sort: {timestamp_ms: -1}});

    if (event && template.subscriptionsReady()) {
      template.markerLayerGroup.clearLayers();

      if (event.type && event.type === 'Distributed') {
        console.log('dist');
        const coords = [];
        event.events.forEach(event => {
          template.markerLayerGroup.addLayer(L.marker([event.lat, event.lng]));
          coords.push([event.lat, event.lng]);
        });
        template.markerLayerGroup.addTo(template.mainMap);

        template.mainMap.fitBounds(coords);
      } else{
        // const markerLayerGroup = L.layerGroup([]);
        // const marker = L.marker([51.5, -0.09]).addTo(mymap);

        template.markerLayerGroup.addLayer(L.marker([event.lat, event.lng])).addTo(template.mainMap);
        template.mainMap.flyTo([event.lat, event.lng], 13);
      }
    }




  });
});