import React from 'react';
import PropTypes from 'prop-types';
import { Marker, Popup } from 'react-leaflet';
import { divIcon } from 'leaflet';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import 'react-leaflet-markercluster/dist/styles.min.css';
import { Loader } from 'semantic-ui-react';
import './boxMapStyle.css';

/** Responsible for the creation, management, and customization of Markers on the Leaflet Map. */
class LeafletMarkerManager extends React.Component {
  constructor(props) {
    super(props);

    // LocationsDict is a mapping of Location.slug => {locationDoc, marker, markerLeafletElement}
    // The value object of this entry consists of the following properties:
    // locationDoc: The Location document.
    // marker: The Marker (React) component representing the Location on the Leaflet map.
    // markerLeafletElement: The Marker component's internal leaflet element object.
    //
    // Note: We need this kind of dictionary because we require a way to store and retrieve a React-Leaflet Marker's
    // internal leaflet marker dom element (we store this as markerLeafletElement), which can only be accessed during
    // the Marker component's instantiation by using a ref callback. See the createMarker() method for details.
    // The React-Leaflet library does not expose the full Leaflet API to us, and so we must have access to the internal
    // leaflet element in order to perform certain operations such as zooming into a marker on the map.
    this.state = {
      locationsDict: {}, // LocationDoc.slug => {locationDoc, marker, markerLeafletElement}
    };
  }

  /**
   * React Lifecycle Methods
   */

  componentDidMount() {
    const { locations = [] } = this.props;
    // Create initial Markers for each passed in Location document.
    this.createMarkers(locations);
  }

  componentDidUpdate() {
    const { locations } = this.props;

    // Create new Marker if does not yet exist, or update existing marker with new data.
    locations.forEach(loc => {
      if (!this.locationExists(loc)) {
        this.createMarker(loc);
      } else {
        this.updateMarker(loc);
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
        : <Loader active content='Loading...'/>;
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

  createMarkers(locations) {
    locations.forEach(loc => this.createMarker(loc));
  }

  createMarker(locationDoc) {
    // Create new object for the dictionary for the given LocationDoc and populate it with the following properties:
    // {locationDoc, marker, markerLeafletElement}. See constructor for more details on these properties.
    // We have to update the dict entry in three stages for each new Location/Marker due how to React-Leaflet works.
    // 1. Create new entry in the Dict for the new Location.slug, store the Location document as 'locationDoc' property.
    // 2. Create a new Marker for the Location, then update entry with a 'marker' property.
    // 3. From the Ref callback, add a 'markerLeafletElement' property to the entry for the newly created Marker.
    this.setLocationsDictEntry(locationDoc.slug, { locationDoc });

    // Get Location coordinates.
    const markerPosition = this.getLocationCoords(locationDoc);
    if (!markerPosition) {
      // eslint-disable-next-line no-console, max-len
      console.log(`Notice: Unable to retrieve location coordinates for location slug: ${locationDoc.slug}. Please ensure that the Locations collection is available and populated in your development environment.`);
      return;
    }

    const newMarker = <Marker
        ref={this.addMarkerLeafletElementToDict.bind(this)(locationDoc)}
        icon={this.locationMarkerIconAndLabel({ locationDoc, iconColor: 'blue' })}
        key={locationDoc.slug}
        locationSlug={locationDoc.slug}
        position={markerPosition}>
      {this.createPopup(locationDoc)}
    </Marker>;

    // Add marker to dictionary.
    this.setLocationsDictEntry(locationDoc.slug, { marker: newMarker });
  }

  updateMarker(locationDoc) {
    // Retrieve locationDoc's corresponding Marker leafletElement, and update it.
    const marker = this.getMarkerLeafletElement(locationDoc);
    if (marker) {
      const newOpts = marker.options; // Don't clone this
      newOpts.icon = this.locationMarkerIconAndLabel({ locationDoc, iconColor: 'blue' });
      marker.refreshIconOptions(newOpts, true);
    }
  }

  markersToRender() {
    const { locations } = this.props;
    // Only display the current subset of locations that were passed in props (even though more may exist in
    // locationsDict)
    const locationMarkers = [];
    locations.forEach(loc => {
      const marker = this.getMarker(loc);
      if (marker) locationMarkers.push(marker);
    });
    return locationMarkers;
  }

  /**
   * Helper Methods
   */

  getLocationCoords(locationDoc) {
    // We're storing coordinates as [lng, lat]. Leaflet Marker requires [lat, lng].
    return locationDoc && locationDoc.coordinates ? locationDoc.coordinates.slice().reverse() : null;
  }

  locationExists(locationDoc) {
    const locations = this.getLocations();
    let exists = false;
    locations.forEach(loc => {
      if (loc.slug === locationDoc.slug) {
        exists = true;
      }
    });
    return exists;
  }

  /**
   * LocationsDict Helpers
   */

  setLocationsDictEntry(locationSlug, locAndMarkersObj) {
    this.setState(prevState => {
      // Always treat state (and prevState) as immutable. (Actually, this might not be enough for nested objects,
      // see: https://stackoverflow.com/questions/43040721/how-to-update-a-nested-state-in-react)
      const currentDict = { ...prevState.locationsDict };
      // FYI: It seems like || {} is not necessary - if currentVal is undefined and we try to spread it, it will simply
      // be ignored. But will keep it like this because it's a bit more clear.
      const currentVal = currentDict[locationSlug] || {};
      const updatedVal = { ...currentVal, ...locAndMarkersObj };
      currentDict[locationSlug] = updatedVal;
      return {
        locationsDict: currentDict,
      };
    });
  }

  getLocations() {
    const { locationsDict } = this.state;
    return Object.values(locationsDict).map(locAndMarkersObj => locAndMarkersObj.locationDoc);
  }

  getMarkers() {
    const { locationsDict } = this.state;
    return Object.values(locationsDict).map(locAndMarkersObj => locAndMarkersObj.marker);
  }

  getMarker(locationDoc) {
    const { locationsDict } = this.state;
    const locAndMarkersObj = locationsDict[locationDoc.slug];
    return (locAndMarkersObj) ? locAndMarkersObj.marker : null;
  }

  getMarkerLeafletElements() {
    const { locationsDict } = this.state;
    return Object.values(locationsDict).map(locAndMarkersObj => locAndMarkersObj.markerLeafletElement);
  }

  getMarkerLeafletElement(locationDoc) {
    const { locationsDict } = this.state;
    const locAndMarkersObj = locationsDict[locationDoc.slug];
    return (locAndMarkersObj) ? locAndMarkersObj.markerLeafletElement : null;
  }

  /**
   * Marker label, Cluster label, and Popup creation methods.
   * The markerLabelFunc, markerPopupFunc, markerClusterLabelFunc, and markerClusterSideLabelFunc prop callback
   * functions are used here to customize the respective displays on the map.
   */

  locationMarkerIconAndLabel({ locationDoc, iconColor = 'blue' }) {
    const { markerLabelFunc } = this.props;

    // Generate marker html
    let markerHtml;
    if (markerLabelFunc) markerHtml = markerLabelFunc(locationDoc);
    else {
      markerHtml = `<div><b>${locationDoc.description}</div>`; // Display location description by default.
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

    // Get Location slugs of all Locations within the cluster.
    const clusterMarkers = cluster.getAllChildMarkers();
    const clusterLocationSlugs = clusterMarkers.map(marker => marker.options.locationSlug);

    // Pass locationSlugs to callback to generate inner cluster display.
    let innerClusterLabelHtml = '';
    if (markerClusterLabelFunc) {
      innerClusterLabelHtml = markerClusterLabelFunc(clusterLocationSlugs);
    } else {
      // If callback not passed, default behavior to to display cluster's location count.
      const locationCount = clusterLocationSlugs.length;
      innerClusterLabelHtml = `<div style='font-size: 26px;'><b>${locationCount}</b></div>`;
    }

    let clusterHtml = `
      <div class="marker-cluster container-fix marker-cluster-blue">
        <div><span>${innerClusterLabelHtml}</span></div>
      </div>`;

    // If present, also pass locationSlugs to side label callback to generate cluster side label display.
    if (markerClusterSideLabelFunc) {
      const sideClusterLabelHtml = markerClusterSideLabelFunc(clusterLocationSlugs);
      clusterHtml += `<div class="marker-cluster-sideLabel">${sideClusterLabelHtml}</div>`;
    }

    return divIcon({
      html: clusterHtml,
      className: 'marker-cluster-container',
      iconSize: [70, 70], // Should be equal to marker-cluster div width (or height) + (margin-left x 2)
    });
  }

  createPopup(locationDoc) {
    const { markerPopupFunc } = this.props;
    if (markerPopupFunc) {
      // Because we are expecting JSX, we call PopupContents as a component with an 'locDoc' prop.
      // Make life easier so the caller doesn't have to pass in an 'locDoc' object prop.
      const PopupContents = ({ locDoc }) => (markerPopupFunc.call(null, locDoc));
      const popup = (
          <Popup offset={[-10, -30]} maxWidth={300}>
            <PopupContents locDoc={locationDoc} />
          </Popup>
      );
      return popup;
    }
    return null;
  }

  /**
   * Event Handling
   */

  zoomToMarker(locationSlug) {
    const { locationsDict } = this.state;
    // Retrieve Marker for the given Location slug
    const marker = locationsDict[locationSlug].markerLeafletElement;
    // Zoom to marker
    this.markerClusterGroupElem.zoomToShowLayer(marker, () => {
      marker.openPopup(); // FYI: Won't throw errors if there is no popup attached to marker.
    });
  }

  /** Ref callbacks */

  // We can only access a Marker's internal leaflet element by using a ref upon the Marker's instantiation. See the
  // createMarker() method for more details.
  addMarkerLeafletElementToDict(locationDoc) {
    return (elem) => {
      // Elem can sometimes be null due to React's normal mounting behavior.
      if (elem) {
        this.setLocationsDictEntry(locationDoc.slug, {
          markerLeafletElement: elem.leafletElement,
        });
      }
    };
  }

  markerClusterGroupRef(elem) {
    // We need to store the MarkerClusterGroup component's leaflet element because the React component does not expose
    // the zoomToShowLayer() method to us.
    // Only need to store ref on initial call, or when we have a new MCG instance - which occurs whenever we pass in a
    // new set of markers to the MCG component. If we do not do this, the zoomToMarker() method will not work
    // because it is pointing to an outdated MCG instance.
    // Note that we always have to check for elem because React calls the ref function twice, with the initial call
    // passing in a null elem value.
    if (elem && !this.markerClusterGroupElem) {
      this.markerClusterGroupElem = elem.leafletElement;
    } else {
      const isNewInstance = (elem) ? elem.leafletElement._leaflet_id !== this.markerClusterGroupElem._leaflet_id
          : false;
      if (elem && isNewInstance) {
        this.markerClusterGroupElem = elem.leafletElement;
      }
    }
  }

}

/**
 * LeafletMarkerManager Component Props
 *
 * locations: The Location docs to display as markers on the map.
 *
 * markerLabelFunc(locationDoc): Creates the marker label for the given Location document. Must return an HTML string.
 * If not supplied, will display Location.description by default.
 *
 * markerPopupFunc(locationDoc): Creates the marker popup contents for the given Location document. Must return JSX. If
 * not supplied, no popup will be displayed by default.
 *
 * markerClusterLabelFunc(locationSlugs): Creates the inner cluster label for the given locationSlugs in that cluster.
 * Must return an HTML string. If not supplied, will display the number of Locations within the cluster.
 *
 * markerClusterSideLabelFunc(locationSlugs): Creates the side cluster label for the given locationSlugs in that
 * cluster. Must return an HTML string. If not supplied, nothing will be displayed by default.
 */
LeafletMarkerManager.propTypes = {
  locations: PropTypes.array.isRequired,
  markerLabelFunc: PropTypes.func,
  markerPopupFunc: PropTypes.func,
  markerClusterLabelFunc: PropTypes.func,
  markerClusterSideLabelFunc: PropTypes.func,
};

// Note: This component does not require withTracker(), as all the data it requires should come from parent component.
export default LeafletMarkerManager;
