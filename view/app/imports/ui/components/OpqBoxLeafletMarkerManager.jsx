import { Meteor } from 'meteor/meteor';
import React from 'react';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import { Marker, Popup } from 'react-leaflet';
import { divIcon } from 'leaflet';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import 'react-leaflet-markercluster/dist/styles.min.css';
import { Loader, List } from 'semantic-ui-react';
import { Measurements } from '../../api/measurements/MeasurementsCollection';
import '../utils/style.css';

class OpqBoxLeafletMarkerManager extends React.Component {
  constructor(props) {
    super(props);

    // OpqBoxAndMarkersDict is a mapping of OpqBox (Mongo) id => {opqBox, marker, markerLeafletElement}
    // Note: We need this kind of dictionary because we require a way to retrieve an OpqBox's markerLeafletElement. Due
    // to the way the react-leaflet package implemented its Marker component, there is no way to access a Marker
    // component's internal leaflet object from outside the component. We can only get a reference to it during the
    // Marker's instantiation (see the createMarker() method).
    // The value object of this dictionary consists of the following properties:
    // opqBox: The OpqBox Mongo document
    // marker: The Marker (React) component representing the OpqBox on the Leaflet map.
    // markerLeafletElement: The Marker component's internal leaflet element object (required for updating the Marker)
    this.state = {
      opqBoxAndMarkersDict: {},
    };
  }

  componentDidMount() {
    const { opqBoxes = [] } = this.props;
    // Create initial Markers for each passed in OpqBox.
    this.createMarkers(opqBoxes);
  }

  componentWillReceiveProps(nextProps) {
    const { opqBoxes } = nextProps;

    // Whenever new box measurements are received via props, we must update Markers.
    opqBoxes.forEach(box => {
      // Create new Marker if does not yet exist, or update existing marker with new data.
      if (!this.opqBoxExists(box)) {
        this.createMarker(box);
      } else {
        this.updateMarker(box);
      }
    });
  }

  updateMarker(opqBox) {
    const { selectedMeasurementType } = this.props;
    // Retrieve box's corresponding Marker leafletElement, and update it.
    const marker = this.state.opqBoxAndMarkersDict[opqBox._id.toHexString()].markerLeafletElement;
    if (marker) {
      const newestMeasurement = this.findNewestMeasurement(opqBox.box_id);
      const rawMeasurementValue = this.filterSelectedMeasurementType(newestMeasurement, selectedMeasurementType, false);
      const formattedMeasurement = this.filterSelectedMeasurementType(newestMeasurement, selectedMeasurementType, true);
      const newOpts = marker.options; // Don't clone this; must modify the original options obj.
      newOpts.rawValue = rawMeasurementValue;
      newOpts.formattedValue = formattedMeasurement;
      const markerHtml = `<div><b>${opqBox.name}<br />${formattedMeasurement}</b></div>`;
      newOpts.icon = this.opqBoxIcon({ markerHtml, opqBox });
      marker.refreshIconOptions(newOpts, true);
    }
  }

  filterSelectedMeasurementType(measurement, measurementType, format = false) {
    const { measurementTypeEnum } = this.props;
    if (!measurement && format) return 'No Data';
    if (!measurement) return null;
    switch (measurementType) {
      case measurementTypeEnum.VOLTAGE_LAYER:
        return (format) ? this.formatMeasurement(measurement.voltage, measurementType) : measurement.voltage;
      case measurementTypeEnum.FREQUENCY_LAYER:
        return (format) ? this.formatMeasurement(measurement.frequency, measurementType) : measurement.frequency;
      case measurementTypeEnum.THD_LAYER:
        return (format) ? this.formatMeasurement(measurement.thd, measurementType) : measurement.thd;
      default:
        return (format) ? this.formatMeasurement(measurement.voltage, measurementType) : measurement.voltage;
    }
  }

  formatMeasurement(value, measurementType) {
    const { measurementTypeEnum } = this.props;
    switch (measurementType) {
      case measurementTypeEnum.VOLTAGE_LAYER:
        return `${value.toFixed(2)} V`;
      case measurementTypeEnum.FREQUENCY_LAYER:
        return `${value.toFixed(3)} Hz`;
      case measurementTypeEnum.THD_LAYER:
        return `${value.toFixed(4)}`;
      default:
        return `${value.toFixed(2)} V`;
    }
  }

  findNewestMeasurement(boxId) {
    const { measurements } = this.props;
    if (measurements.length) {
      // Measurements are already sorted before being passed to the BoxMap component, so Array.find() is appropriate.
      return measurements.find(measurement => measurement.box_id === boxId);
    }
    return null;
  }

  opqBoxExists(opqBox) {
    const boxes = this.getOpqBoxes();
    let exists = false;
    boxes.forEach(box => {
      if (box.box_id === opqBox.box_id) {
        exists = true;
      }
    });
    return exists;
  }

  getOpqBoxes() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.opqBox);
  }

  getMarkers() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.marker);
  }

  getMarkerLeafletElements() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.markerLeafletElement);
  }

  addMarkerLeafletElementToDict(opqBox) {
    return (ref) => {
      this.createOrUpdateOpqBoxAndMarkersDictEntry(opqBox._id.toHexString(), {
        markerLeafletElement: ref.leafletElement,
      });
    };
  }

  opqBoxIcon({ markerHtml, opqBox }) {
    const { selectedMeasurementType } = this.props;
    const newestMeasurement = this.findNewestMeasurement(opqBox.box_id);
    const selectedMeasurement = this.filterSelectedMeasurementType(newestMeasurement, selectedMeasurementType);
    const quality = this.calculateDataQuality(selectedMeasurement);
    let className = 'opqBoxMarker '; // Note the trailing space.
    if (quality === 'good') {
      className += 'blue';
    } else if (quality === 'mediocre') {
      className += 'yellow';
    } else if (quality === 'poor') {
      className += 'red';
    }

    return divIcon({
      html: markerHtml,
      className: className,
      iconSize: [40, 40],
      iconAnchor: [32, 40],
    });
  }

  clusterIcon(cluster) {
    const { selectedMeasurementType = '' } = this.props;
    const children = cluster.getAllChildMarkers();
    let total = 0;
    let clusterActiveBoxesCount = children.length;
    children.forEach(child => {
      const value = Number(child.options.rawValue);
      if (value) { // Reminder: When rawValue = null, Number(null) == 0 == falsy.
        total += value;
      } else {
        clusterActiveBoxesCount--;
      }
    });

    const avg = (clusterActiveBoxesCount) ? total / clusterActiveBoxesCount : 0;
    const formattedAvg = this.formatMeasurement(avg, selectedMeasurementType);
    const className = this.clusterIconCssClass(avg);

    return divIcon({
      html: `<div><span><b>${formattedAvg}</b></span></div>`,
      className: `marker-cluster ${className}`,
      iconSize: [70, 70], // Should be equal to marker-cluster div width (or height) + margin-left + margin-right
    });
  }

  clusterIconCssClass(value) {
    const quality = this.calculateDataQuality(value);
    let className = 'marker-cluster-';
    if (quality === 'poor') {
      className += 'red';
    } else if (quality === 'mediocre') {
      className += 'yellow';
    } else if (quality === 'good') {
      className += 'blue';
    }
    return className;
  }

  calculateDataQuality(value) {
    const { selectedMeasurementType, measurementTypeEnum } = this.props;
    let quality = null; // Can be 'poor', 'mediocre', or 'good'.
    switch (selectedMeasurementType) {
      case measurementTypeEnum.VOLTAGE_LAYER: {
        const NOMINAL = 120;
        const MULTIPLIER = 0.05;
        const HALF_MULTIPLIER = MULTIPLIER / 2.0;
        if (value < NOMINAL * (1.0 - MULTIPLIER) || value > NOMINAL * (1.0 + MULTIPLIER)) {
          quality = 'poor';
        } else if (value < NOMINAL * (1.0 - HALF_MULTIPLIER) || value > NOMINAL * (1.0 + HALF_MULTIPLIER)) {
          quality = 'mediocre';
        } else {
          quality = 'good';
        }
        break;
      }
      case measurementTypeEnum.FREQUENCY_LAYER: {
        const NOMINAL = 60;
        const MULTIPLIER = 0.05;
        const HALF_MULTIPLIER = MULTIPLIER / 2.0;
        if (value < NOMINAL * (1.0 - MULTIPLIER) || value > NOMINAL * (1.0 + MULTIPLIER)) {
          quality = 'poor';
        } else if (value < NOMINAL * (1.0 - HALF_MULTIPLIER) || value > NOMINAL * (1.0 + HALF_MULTIPLIER)) {
          quality = 'mediocre';
        } else {
          quality = 'good';
        }
        break;
      }
      case measurementTypeEnum.THD_LAYER: {
        // Found these values by just looking at trends data. Need to find out official values.
        if (value < 0.005 || value > 0.05) {
          quality = 'poor';
        } else if (value < 0.01 || value > 0.04) {
          quality = 'mediocre';
        } else {
          quality = 'good';
        }
        break;
      }
      default: {
        break;
      }
    }
    return quality;
  }

  createMarkers(opqBoxes) {
    opqBoxes.forEach(opqBox => this.createMarker(opqBox));
  }

  createMarker(opqBox) {
    const { zipcodeLatLngDict } = this.props;
    // Create new object for the dictionary for the given OpqBox and populate it with the following properties:
    // {opqBox, marker, markerLeafletElement}. See constructor for more details on these properties.

    // We have to update the dict entry in three stages for each new Box/Marker due how to React-Leaflet works.
    // 1. Create new entry in the Dict for the new box id, store the OpqBox document as 'opqBox' property.
    // 2. Create a new Marker for the Box, then update entry with a 'marker' property.
    // 3. From the Ref callback, add a 'markerLeafletElement' property to the entry for the newly created Marker.
    this.createOrUpdateOpqBoxAndMarkersDictEntry(opqBox._id.toHexString(), { opqBox });
    const initialMarkerHtml = `<div><b>${opqBox.name}</div>`;
    const markerPosition = this.getOpqBoxLocation(opqBox);
    console.log('markerposition: ', opqBox, markerPosition);
    const newMarker = <Marker
                        ref={this.addMarkerLeafletElementToDict.bind(this)(opqBox)}
                        // icon={this.opqBoxIcon(initialMarkerHtml)}
                        icon={this.opqBoxIcon({ markerHtml: initialMarkerHtml, opqBox })}
                        key={opqBox._id}
                        rawValue=''
                        formattedValue=''
                        position={markerPosition}>
                        <Popup offset={[-10, -30]} maxWidth={300}>
                          {this.popupContents(opqBox)}
                        </Popup>
                      </Marker>;

    this.createOrUpdateOpqBoxAndMarkersDictEntry(opqBox._id.toHexString(), { marker: newMarker });
  }

  getOpqBoxLocation(opqBox) {
    const { zipcodeLatLngDict } = this.props;
    console.log('Zipcdoe Dict ', zipcodeLatLngDict);
    if (opqBox.locations) {
      const latlng = zipcodeLatLngDict[opqBox.locations[opqBox.locations.length - 1].zipcode];
      console.log(latlng);
      // In rare cases, opqBox will have a zipcode, but its an invalid one and thus not in our zipcodeDict.
      return latlng || [25.0, -71.0];
    }
    return [25.0, -71.0]; // Temporary location for marker if no location information available.
  }

  popupContents(opqBox) {
    return (
        <List divided style={{ width: '250px' }}>
          <List.Item>
            <List.Icon name='disk outline' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Box Name</i></List.Header>
              <List.Description>{opqBox.name}</List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Location</i></List.Header>
              <List.Description>UH Manoa Holmes Hall 314</List.Description>
              <List.Description>{this.getOpqBoxLocation(opqBox).toString()}</List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='tag' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Description</i></List.Header>
              <List.Description>{opqBox.description}</List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='plug' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Unplugged Status</i></List.Header>
              <List.Description>{opqBox.unplugged.toString()}</List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='creative commons' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Calibration Constant</i></List.Header>
              <List.Description>{opqBox.calibration_constant}</List.Description>
            </List.Content>
          </List.Item>
        </List>
    );
  }

  createOrUpdateOpqBoxAndMarkersDictEntry(boxIdString, opqBoxAndMarkersObj) {
    this.setState(prevState => {
      // Always treat state (and prevState) as immutable. (Actually, this might not be enough for nested objects,
      // see: https://stackoverflow.com/questions/43040721/how-to-update-a-nested-state-in-react)
      const currentDict = { ...prevState.opqBoxAndMarkersDict };
      // FYI: It seems like || {} is not necessary - if currentVal is undefined and we try to spread it, it will simply
      // be ignored. But will keep it like this because it's a bit more clear.
      const currentVal = currentDict[boxIdString] || {};
      const updatedVal = { ...currentVal, ...opqBoxAndMarkersObj };
      currentDict[boxIdString] = updatedVal;
      return {
        opqBoxAndMarkersDict: currentDict,
      };
    });
  }

  zoomToMarker(box_id) {
    const { opqBoxAndMarkersDict } = this.state;
    // Retrieve Marker for the given OpqBox
    const marker = opqBoxAndMarkersDict[box_id].markerLeafletElement;
    // Zoom to marker, open its Popup
    this.markerClusterGroupRefElem.zoomToShowLayer(marker, () => {
      marker.openPopup(); // Trigger marker's Popup after zoom is completed.
    });
  }

  render() {
    // Render when props are ready and Markers have been created.
    return (this.props.ready && this.getMarkers().length)
        ? this.renderPage()
        : <Loader active content='Retrieving data...'/>;
  }

  markerClusterGroupRef(elem) {
    // Ensure we only set this once.
    if (!this.markerClusterGroupRefElem && elem) {
      // console.log('ScrollableControl ref elem: ', elem);
      this.markerClusterGroupRefElem = elem.leafletElement; // Just store the leaflet element itself.
      console.log('Adding markerClusterGroupRefElem: ', elem);
    }
  }

  renderPage() {
    return (
        <MarkerClusterGroup
            ref={this.markerClusterGroupRef.bind(this)}
            animate={true}
            spiderfyDistanceMultiplier={3}
            iconCreateFunction={this.clusterIcon.bind(this)}
            onSpiderfied={(cluster, markers) => console.log(cluster, markers, cluster.getAllChildMarkers())}>
          {this.getMarkers()}
        </MarkerClusterGroup>
    );
  }

}

OpqBoxLeafletMarkerManager.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  zipcodeLatLngDict: PropTypes.object.isRequired,
  measurements: PropTypes.array.isRequired,
  selectedMeasurementType: PropTypes.string.isRequired,
  measurementTypeEnum: PropTypes.object.isRequired,
};

export default withTracker(props => {
  const { opqBoxes = [], zipcodeLatLngDict, childRef } = props;
  const measurementsSub = Meteor.subscribe(
      Measurements.publicationNames.BOX_MAP_MEASUREMENTS,
      opqBoxes.map(box => box.box_id),
  );
  return {
    ready: measurementsSub.ready(),
    opqBoxes,
    zipcodeLatLngDict,
    measurements: Measurements.find({}, { sort: { timestamp_ms: -1 } }).fetch(),
    ref: childRef,
  };
})(OpqBoxLeafletMarkerManager);
