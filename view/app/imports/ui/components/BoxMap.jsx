import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { Loader } from 'semantic-ui-react';
import 'semantic-ui-css/semantic.css';
import Lodash from 'lodash';
import { Map, TileLayer, LayerGroup, LayersControl } from 'react-leaflet';
import { withTracker } from 'meteor/react-meteor-data';
import { withStateContainer } from '../utils/hocs';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { getZipcodeLatLng } from '../../api/zipcodes/ZipcodesCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';
import OpqBoxLeafletMarkerManager from './OpqBoxLeafletMarkerManager';

const { BaseLayer } = LayersControl;

class BoxMap extends React.Component {
  constructor(props) {
    super(props);

    this.mapLayerNames = {
      VOLTAGE_LAYER: 'voltage_layer',
      FREQUENCY_LAYER: 'frequency_layer',
      THD_LAYER: 'thd_layer',
    };

    this.state = {
      activeBoxIds: [],
      mostRecentBoxMeasurements: [],
      locations: {},
      currentMapLayer: this.mapLayerNames.VOLTAGE_LAYER,
    };


    this.handleBaselayerchange.bind(this);
    this.handleOverlayadd.bind(this);
    this.handleOverlayremove.bind(this);
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active content='Retrieving data...'/>;
  }

  handleBaselayerchange(e) {
    const mapLayerNames = this.mapLayerNames;
    switch (e.name) {
      case mapLayerNames.VOLTAGE_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.VOLTAGE_LAYER });
        break;
      case mapLayerNames.FREQUENCY_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.FREQUENCY_LAYER });
        break;
      case mapLayerNames.THD_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.THD_LAYER });
        break;
      default:
        console.log('Unknown MapLayerName type.');
        break;
    }
  }

  handleOverlayadd(e) {
    const mapLayerNames = this.mapLayerNames;
    switch (e.name) {
      case mapLayerNames.VOLTAGE_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.VOLTAGE_LAYER });
        break;
      case mapLayerNames.FREQUENCY_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.FREQUENCY_LAYER });
        break;
      case mapLayerNames.THD_LAYER:
        this.setState({ currentMapLayer: mapLayerNames.THD_LAYER });
        break;
      default:
        console.log('Unknown MapLayerName type.');
        break;
    }
  }

  handleOverlayremove(e) {
    console.log('Overlay Remove: ', e, e.layer, e.name);
  }

  renderPage() {
    const { opqBoxes, zipcodeLatLngDict } = this.props;
    const firstZipcode = Object.keys(zipcodeLatLngDict).reverse()[0]; // Reverse so Hawaii zipcodes first.
    const center = (firstZipcode) ? zipcodeLatLngDict[firstZipcode] : [21.31, -157.86]; // Default view on Oahu.

    return (
        <WidgetPanel title="Box Map">
          <Map onBaselayerchange={this.handleBaselayerchange.bind(this)}
               onOverlayadd={this.handleOverlayadd}
               onOverlayremove={this.handleOverlayremove}
               center={center}
               zoom={11}
               style={{ height: 600 }}>
            <TileLayer
                attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <LayersControl>
              <BaseLayer checked name={this.mapLayerNames.VOLTAGE_LAYER}>
                <LayerGroup>
                  <OpqBoxLeafletMarkerManager
                      opqBoxes={opqBoxes}
                      zipcodeLatLngDict={zipcodeLatLngDict}
                      selectedMeasurementType={this.state.currentMapLayer}
                      measurementTypeEnum={this.mapLayerNames} />
                </LayerGroup>
              </BaseLayer>
            </LayersControl>
          </Map>
        </WidgetPanel>
    );
  }
}

BoxMap.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  zipcodeLatLngDict: PropTypes.object.isRequired,
};

// Parent/Container state object that will wrap the withTracker HOC via the withStateContainer HOC.
// (See ui/utils/hocs.jsx for usage/further explanation).
const containerState = {
  methodCallsComplete: false,
  zipcodeLatLngDict: {},
};

// The function that will be passed to the withTracker HOC.
const withTrackerCallback = props => {
  const { zipcodeLatLngDict, methodCallsComplete } = props;
  // Even though this subscription correctly retrieves only the currently logged in user's boxes, remember that
  // Minimongo merges any other OpqBox documents from other OpqBox subscriptions (even from other currently rendered
  // React components!) into the same client side collection.
  // Therefore, it's not always enough to simply subscribe to a publication - we sometimes have to follow it up with
  // another Mongo query on the client side to make sure we are working with the correct subset of documents.

  // While it might seem strange to be subscribing to the BoxOwners collection here, especially since the
  // GET_CURRENT_USER_OPQ_BOXES subscription correctly only returns the current user's opq boxes - because of the
  // problems described above about Minimongo, we must be sure to filter out OpqBox documents that might exist
  // in the client side collection that do not belong to the currently logged in user.
  // There are two approaches that I see:
  // 1. Use a Meteor method call that uses findBoxIdsWithOwner() to check which OpqBoxes belong to the user.
  // 2. Subscribe to the BoxOwners collection, also using the findBoxIdsWithOwner() method to check OpqBox ownership.
  //
  // Both techniques will do the job, but approach #2 will give us a more reactive result, because if any BoxOwner
  // documents are added/modified/removed on the server, it will trigger this withTracker function (a reactive data
  // source) to rerun - thereby updating the UI reactively.
  // The Meteor method approach will not give us this level of reactivity (that is, a BoxOwner document change will not
  // trigger a Tracker re-run on the client), though it may be a simpler approach overall to implement and can be
  // used if we do not care about fine-tuned reactivity.
  const opqBoxesSub = Meteor.subscribe(OpqBoxes.publicationNames.GET_CURRENT_USER_OPQ_BOXES);
  const boxOwnersSub = Meteor.subscribe(BoxOwners.publicationNames.GET_CURRENT_USER_BOX_OWNERS);
  const currentUser = Meteor.user();
  let opqBoxes = [];
  if (currentUser) {
    const boxIds = BoxOwners.findBoxIdsWithOwner(currentUser.username);
    opqBoxes = OpqBoxes.find({ box_id: { $in: boxIds } }).fetch();
  }

  // Once OpqBoxes subscriptions ready, we make Meteor method calls to retrieve OpqBox lat-lng (from their zipcode).
  if (opqBoxesSub.ready() && boxOwnersSub.ready() && !methodCallsComplete) {
    let numCallsRemaining = opqBoxes.length;
    // If no boxes for user, mark as complete immediately.
    if (opqBoxes.length === 0) props.setContainerState({ methodCallsComplete: true });
    opqBoxes.forEach(box => {
      const zipcode = box.locations[box.locations.length - 1].zipcode;
      getZipcodeLatLng.call({ zipcode }, (error, zipcodeDoc) => {
        --numCallsRemaining;
        if (error) console.log(error);
        else {
          const currentZipcodes = zipcodeLatLngDict;
          currentZipcodes[zipcodeDoc.zipcode] = [zipcodeDoc.latitude, zipcodeDoc.longitude];
          props.setContainerState({ zipcodeLatLngDict: currentZipcodes });
          if (numCallsRemaining === 0) props.setContainerState({ methodCallsComplete: true });
        }
      });
    });
  }

  return {
    ready: opqBoxesSub.ready() && boxOwnersSub.ready() && methodCallsComplete,
    opqBoxes: opqBoxes,
    zipcodeLatLngDict: zipcodeLatLngDict,
  };
};

// Component composition.
export default Lodash.flowRight([
  withStateContainer(containerState),
  withTracker(withTrackerCallback),
])(BoxMap);
