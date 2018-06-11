import React from 'react';
import PropTypes from 'prop-types';
import { Marker, Popup } from 'react-leaflet';
import { divIcon } from 'leaflet';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import 'react-leaflet-markercluster/dist/styles.min.css';
import { Loader } from 'semantic-ui-react';
import './boxMapStyle.css';

/** Responsible for the creation, management, and customization of OpqBox Markers on the Map. */
class OpqBoxLeafletMarkerManager extends React.Component {
  constructor(props) {
    super(props);

    // OpqBoxAndMarkersDict is a mapping of OpqBox.box_id => {opqBox, marker, markerLeafletElement}
    // The value object of this entry consists of the following properties:
    // opqBox: The OpqBox document.
    // marker: The Marker (React) component representing the OpqBox on the Leaflet map.
    // markerLeafletElement: The Marker component's internal leaflet element object.
    //
    // Note: We need this kind of dictionary because we require a way to retrieve an OpqBox's markerLeafletElement,
    // which can only be accessed during the Marker component's instantiation by using a ref callback. See the
    // createMarker() method for details. The React-Leaflet library does not expose the full Leaflet API to us, and
    // so we must have access to the internal leaflet element in order to perform certain operations such as zooming
    // into a marker on the map.
    this.state = {
      opqBoxAndMarkersDict: {},
    };
  }

  /**
   * React Lifecycle Methods
   */

  componentDidMount() {
    const { opqBoxes = [] } = this.props;
    // Create initial Markers for each passed in OpqBox.
    this.createMarkers(opqBoxes);
  }

  componentDidUpdate() {
    const { opqBoxes } = this.props;

    // Create new Marker if does not yet exist, or update existing marker with new data.
    opqBoxes.forEach(box => {
      if (!this.opqBoxExists(box)) {
        this.createMarker(box);
      } else {
        this.updateMarker(box);
      }
    });
  }

  /**
   * Render Methods
   */

  render() {
    // Render after Marker creation
    return (this.getMarkers().length)
        ? this.renderPage()
        : <Loader active content='Retrieving data...'/>;
  }

  renderPage() {
    return (
        <MarkerClusterGroup
            ref={this.markerClusterGroupRef.bind(this)}
            animate={true}
            maxClusterRadius={100}
            spiderfyDistanceMultiplier={6}
            iconCreateFunction={this.clusterIconAndLabel.bind(this)}>
          {this.markersToRender()}
        </MarkerClusterGroup>
    );
  }

  /**
   * Marker management methods
   */

  createMarkers(opqBoxes) {
    opqBoxes.forEach(opqBox => this.createMarker(opqBox));
  }

  createMarker(opqBox) {
    // Create new object for the dictionary for the given OpqBox and populate it with the following properties:
    // {opqBox, marker, markerLeafletElement}. See constructor for more details on these properties.
    // We have to update the dict entry in three stages for each new Box/Marker due how to React-Leaflet works.
    // 1. Create new entry in the Dict for the new box id, store the OpqBox document as 'opqBox' property.
    // 2. Create a new Marker for the Box, then update entry with a 'marker' property.
    // 3. From the Ref callback, add a 'markerLeafletElement' property to the entry for the newly created Marker.
    this.setOpqBoxAndMarkersDictEntry(opqBox.box_id, { opqBox });

    // Get Box coordinates.
    const markerPosition = this.getBoxLatLng(opqBox);
    if (!markerPosition) {
      // eslint-disable-next-line no-console, max-len
      console.log(`Notice: Unable to retrieve location coordinates for box_id: ${opqBox.box_id}. Please ensure that the Locations collection is available and populated in your development environment.`);
      return;
    }

    const newMarker = <Marker
        ref={this.addMarkerLeafletElementToDict.bind(this)(opqBox)}
        icon={this.opqBoxMarkerIconAndLabel({ opqBox, iconColor: 'blue' })}
        key={opqBox.box_id}
        box_id={opqBox.box_id}
        position={markerPosition}>
      {this.createPopup(opqBox)}
    </Marker>;

    // Add marker to dictionary.
    this.setOpqBoxAndMarkersDictEntry(opqBox.box_id, { marker: newMarker });
  }

  updateMarker(opqBox) {
    // Retrieve box's corresponding Marker leafletElement, and update it.
    const marker = this.getMarkerLeafletElement(opqBox);
    if (marker) {
      const newOpts = marker.options; // Don't clone this
      newOpts.icon = this.opqBoxMarkerIconAndLabel({ opqBox, iconColor: 'blue' });
      marker.refreshIconOptions(newOpts, true);
    }
  }

  markersToRender() {
    const { opqBoxes } = this.props;

    // Only display the current subset of opqBoxes that were passed in props (even though more may exist in
    // opqBoxMarkersDict)
    const boxMarkers = [];
    opqBoxes.forEach(box => {
      const marker = this.getMarker(box);
      if (marker) boxMarkers.push(marker);
    });
    return boxMarkers;
  }

  /**
   * Helper Methods
   */

  getBoxLatLng(opqBox) {
    const boxLocationDoc = this.getOpqBoxLocationDoc(opqBox);
    if (boxLocationDoc) {
      // We're storing coordinates as [lng, lat]. Leaflet Marker requires [lat, lng].
      return boxLocationDoc.coordinates.slice().reverse();
    }
    return null;
  }

  getOpqBoxLocationDoc(opqBox) {
    const { locations } = this.props;
    return locations.find(location => opqBox.location === location.slug);
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

  /**
   * OpqBoxAndMarkersDict Helpers
   */

  setOpqBoxAndMarkersDictEntry(boxId, opqBoxAndMarkersObj) {
    this.setState(prevState => {
      // Always treat state (and prevState) as immutable. (Actually, this might not be enough for nested objects,
      // see: https://stackoverflow.com/questions/43040721/how-to-update-a-nested-state-in-react)
      const currentDict = { ...prevState.opqBoxAndMarkersDict };
      // FYI: It seems like || {} is not necessary - if currentVal is undefined and we try to spread it, it will simply
      // be ignored. But will keep it like this because it's a bit more clear.
      const currentVal = currentDict[boxId] || {};
      const updatedVal = { ...currentVal, ...opqBoxAndMarkersObj };
      currentDict[boxId] = updatedVal;
      return {
        opqBoxAndMarkersDict: currentDict,
      };
    });
  }

  getOpqBoxes() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.opqBox);
  }

  getOpqBox(box_id) {
    const { opqBoxAndMarkersDict } = this.state;
    return opqBoxAndMarkersDict[box_id];
  }

  getMarkers() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.marker);
  }

  getMarker(opqBox) {
    const { opqBoxAndMarkersDict } = this.state;
    const boxEntry = opqBoxAndMarkersDict[opqBox.box_id];
    return (boxEntry) ? boxEntry.marker : null;
  }

  getMarkerLeafletElements() {
    const { opqBoxAndMarkersDict } = this.state;
    return Object.values(opqBoxAndMarkersDict).map(boxAndMarkers => boxAndMarkers.markerLeafletElement);
  }

  getMarkerLeafletElement(opqBox) {
    const { opqBoxAndMarkersDict } = this.state;
    const boxEntry = opqBoxAndMarkersDict[opqBox.box_id];
    return (boxEntry) ? boxEntry.markerLeafletElement : null;
  }

  /**
   * Marker label, Cluster label, and Popup creation methods.
   * The boxMarkerLabelFunc, boxMarkerPopupFunc, markerClusterLabelFunc, and markerClusterSideLabelFunc prop callback
   * functions are used here to customize the respective displays on the map.
   */

  opqBoxMarkerIconAndLabel({ opqBox, iconColor = 'blue' }) {
    const { boxMarkerLabelFunc } = this.props;

    // Generate marker html
    let markerHtml;
    if (boxMarkerLabelFunc) markerHtml = boxMarkerLabelFunc(opqBox);
    else {
      markerHtml = `<div><b>${opqBox.name}</div>`; // Just show box name by default.
    }

    // Select icon color.
    let className = 'opqBoxMarker '; // Note the trailing space.
    switch (iconColor) {
      case 'blue':
        className += 'blue';
        break;
      case 'yellow':
        className += 'yellow';
        break;
      case 'red':
        className += 'red';
        break;
      default:
        className += 'blue';
        break;
    }

    return divIcon({
      html: markerHtml,
      className: className,
      iconSize: [40, 40],
      iconAnchor: [32, 40],
    });
  }

  clusterIconAndLabel(cluster) {
    const { markerClusterLabelFunc, markerClusterSideLabelFunc } = this.props;

    // Get BoxIds of all boxes within the cluster.
    const clusterMarkers = cluster.getAllChildMarkers();
    const clusterBoxIds = clusterMarkers.map(marker => marker.options.box_id);

    // Pass boxIds to callback to generate inner cluster display.
    let innerClusterLabelHtml = '';
    if (markerClusterLabelFunc) {
      innerClusterLabelHtml = markerClusterLabelFunc(clusterBoxIds);
    } else {
      // If callback not passed, default behavior to to display cluster's box count.
      const boxCount = clusterBoxIds.length;
      innerClusterLabelHtml = `<div style='font-size: 26px;'><b>${boxCount}</b></div>`;
    }

    let clusterHtml = `
      <div class="marker-cluster container-fix marker-cluster-blue">
        <div><span>${innerClusterLabelHtml}</span></div>
      </div>`;

    // If present, also pass boxIds to side label callback to generate cluster side label display.
    if (markerClusterSideLabelFunc) {
      const sideClusterLabelHtml = markerClusterSideLabelFunc(clusterBoxIds);
      clusterHtml += `<div class="marker-cluster-sideLabel">${sideClusterLabelHtml}</div>`;
    }

    return divIcon({
      html: clusterHtml,
      className: 'marker-cluster-container',
      iconSize: [70, 70], // Should be equal to marker-cluster div width (or height) + (margin-left x 2)
    });
  }

  createPopup(opqBox) {
    const { boxMarkerPopupFunc } = this.props;
    if (boxMarkerPopupFunc) {
      // Because we are expecting JSX, we call PopupContents as a component with an 'opqBoxDoc' prop.
      // Make life easier so the caller doesn't have to pass in an 'opqBoxDoc' object prop.
      const PopupContents = ({ opqBoxDoc }) => (boxMarkerPopupFunc.call(null, opqBoxDoc));
      const popup = (
          <Popup offset={[-10, -30]} maxWidth={300}>
            <PopupContents opqBoxDoc={opqBox} />
          </Popup>
      );
      return popup;
    }
    return null;
  }

  /**
   * Event Handling
   */

  zoomToMarker(box_id) {
    const { opqBoxAndMarkersDict } = this.state;
    // Retrieve Marker for the given OpqBox
    const marker = opqBoxAndMarkersDict[box_id].markerLeafletElement;
    // Zoom to marker
    this.markerClusterGroupRefElem.zoomToShowLayer(marker, () => {
      marker.openPopup(); // FYI: Won't throw errors if there is no popup attached to marker.
    });
  }

  /** Ref callbacks */

  // We can only access a Marker's internal leaflet element by using a ref upon the Marker's instantiation. See the
  // createMarker() method for more details.
  addMarkerLeafletElementToDict(opqBox) {
    return (elem) => {
      // Elem can sometimes be null due to React's normal mounting behavior.
      if (elem) {
        this.setOpqBoxAndMarkersDictEntry(opqBox.box_id, {
          markerLeafletElement: elem.leafletElement,
        });
      }
    };
  }

  markerClusterGroupRef(elem) {
    // We need to store the MarkerClusterGroup component's leaflet element because the React component does not expose
    // the zoomToShowLayer() method to us.
    // Only need to store ref on initial call, or when we have a new MCG instance - which occurs whenever we pass in a
    // new set of OpqBox markers to the MCG component. If we do not do this, the zoomToMarker() method will not work
    // because it is pointing to an outdated MCG instance.
    // Note that we always have to check for elem because React calls the ref function twice, with the initial call
    // passing in a null elem value.
    if (elem && !this.markerClusterGroupRefElem) {
      this.markerClusterGroupRefElem = elem.leafletElement;
    } else {
      const isNewInstance = (elem) ? elem.leafletElement._leaflet_id !== this.markerClusterGroupRefElem._leaflet_id
          : false;
      if (elem && isNewInstance) {
        this.markerClusterGroupRefElem = elem.leafletElement;
      }
    }
  }

}

/**
 * OpqBoxLeafletMarkerManager Component Props
 *
 * opqBoxes: The OpqBox docs to display as markers on the map.
 *
 * locations: The location docs associated with the given opqBoxes.
 *
 * boxMarkerLabelFunc(opqBox): Creates the box marker label for the given OpqBox document. Must return an HTML string.
 * If not supplied, will display the box name by default.
 *
 * boxMarkerPopupFunc(opqBox): Creates the marker popup contents for the given OpqBox document. Must return JSX. If
 * not supplied, no popup will be displayed by default.
 *
 * markerClusterLabelFunc(box_ids): Creates the inner cluster label for the given box_ids in that cluster. Must return
 * an HTML string. If not supplied, will display the number of boxes within the cluster.
 *
 * markerClusterSideLabelFunc(box_ids): Creates the side cluster label for the given box_ids in that cluster. Must
 * return an HTML string. If not supplied, nothing will be displayed by default.
 */
OpqBoxLeafletMarkerManager.propTypes = {
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
  boxMarkerLabelFunc: PropTypes.func,
  boxMarkerPopupFunc: PropTypes.func,
  markerClusterLabelFunc: PropTypes.func,
  markerClusterSideLabelFunc: PropTypes.func,
};

// Note: This component does not require withTracker(), as all the data it requires should come from parent component.
export default OpqBoxLeafletMarkerManager;
