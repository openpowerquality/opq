import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { Loader, Form, Checkbox, Button, Icon, Popup, Item, List, Transition } from 'semantic-ui-react';
// import 'semantic-ui-css/semantic.css';
import Lodash from 'lodash';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import Control from 'react-leaflet-control';
import { withTracker } from 'meteor/react-meteor-data';
import { withStateContainer } from '../utils/hocs';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { Locations } from '../../api/locations/LocationsCollection';
import { Regions } from '../../api/regions/RegionsCollection';
import { getZipcodeLatLng } from '../../api/zipcodes/ZipcodesCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';
import OpqBoxLeafletMarkerManager from './OpqBoxLeafletMarkerManager';
import ScrollableControl from '../utils/ScrollableControl';

class BoxMap extends React.Component {
  constructor(props) {
    super(props);

    this.mapDataDisplayTypes = {
      VOLTAGE_DATA: 'voltage_data',
      FREQUENCY_DATA: 'frequency_data',
      THD_DATA: 'thd_data',
    };

    this.mapLocationGranularityTypes = {
      BOX_LOCATION: 'box_location',
      BOX_REGION: 'box_region',
    };

    this.state = {
      currentMapDataDisplay: this.mapDataDisplayTypes.VOLTAGE_DATA,
      currentMapLocationGranularity: this.mapLocationGranularityTypes.BOX_LOCATION,
      expandedItemBoxId: '', // Refers to the most recently selected Box in the map side panel listing of boxes.
    };
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active content='Retrieving data...'/>;
  }

  sidePanel(opqBoxes) {
    // Want side panel height to be equal to Map component height. Since Map can be set to 100% height, we dynamically
    // measure the height (set in state) and use that value for the sidePanel div height.
    const { mapHeight = 600 } = this.state;
    return (
      <div
          className='mapListShadow'
          style={{ height: `${mapHeight}px`, width: '300px', marginLeft: '-10px', marginTop: '-10px',
                    overflow: 'auto', backgroundColor: '#f9f9f9' }}>
        {this.opqBoxItemGroup(opqBoxes)}
      </div>
    );
  }

  opqBoxItemGroup(opqBoxes) {
    const opqBoxItems = opqBoxes.map(box => this.opqBoxItem(box));
    return (
        <Item.Group divided style={{ paddingTop: '10px', paddingBottom: '10px' }}>
          {opqBoxItems}
        </Item.Group>
    );
  }

  handleDetailsButtonClick(opqBox) {
    this.setState({ expandedItemBoxId: opqBox.box_id });
  }

  handleZoomButtonClick(box_id) {
    // Since we stored a ref to the OpqBoxLeafletMarkerManager child component, we can call its zoomToMarker method.
    // This is the simplest way to accomplish this task, because the OpqBoxLeafletMarkerManager component maintains
    // the list of Map markers, not this component.
    this.opqBoxLeafletMarkerManagerRefElem.zoomToMarker(box_id);
  }

  opqBoxDetailsList(opqBox) {
    const boxLocationDoc = this.getOpqBoxLocationDoc(opqBox);
    return (
        <List divided style={{ width: '250px' }}>
          <List.Item>
            <List.Icon name='desktop' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Box Name</i></List.Header>
              <List.Description>{opqBox.name}</List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Location</i></List.Header>
              <List.Description>{boxLocationDoc.description}</List.Description>
              <List.Description>{boxLocationDoc.slug}</List.Description>
              <List.Description>
                {`[${boxLocationDoc.coordinates[0]}, ${boxLocationDoc.coordinates[1]}]`}
              </List.Description>
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

  opqBoxItem(opqBox) {
    const { expandedItemBoxId } = this.state;
    const h2classname = (opqBox.box_id.length > 1) ? 'small' : 'large';

    const mainItem = (
        <Item key={opqBox.box_id}>
          <div className='mapListingBoxId'><h2 className={h2classname}>{opqBox.box_id}</h2></div>
          <Item.Content>
            <Item.Header>{opqBox.name}</Item.Header>
            <Item.Description style={{ marginTop: '0px' }}>
              {this.getOpqBoxLocationDoc(opqBox).description}
            </Item.Description>
            <Item.Extra>
              <Button.Group basic size='tiny'>
                <Popup
                    trigger={
                      <Button icon onClick={this.handleZoomButtonClick.bind(this, opqBox._id.toHexString())}>
                        <Icon size='large' name='crosshairs' />
                      </Button>
                    }
                    content='Zoom to box location'
                />
                <Popup
                    trigger={
                      <Button icon onClick={this.handleDetailsButtonClick.bind(this, opqBox)}>
                        <Icon size='large' name='list' />
                      </Button>
                    }
                    content='View additional box details'
                />
                <Popup
                    trigger={
                      <Button icon>
                        <Icon size='large' name='setting' />
                      </Button>
                    }
                    content='Box Settings'
                />
                <Popup
                    trigger={
                      <Button icon>
                        <Icon size='large' name='lightning' />
                      </Button>
                    }
                    content='View box events'
                />
                <Popup
                    trigger={
                      <Button icon>
                        <Icon size='large' name='line chart' />
                      </Button>
                    }
                    content='View box measurements and trends'
                />
              </Button.Group>
            </Item.Extra>
          </Item.Content>
        </Item>
    );

    const isVisible = expandedItemBoxId === opqBox.box_id;
    const fullBoxDetails = (
        <Transition
            key={`${opqBox.box_id}_details`}
            unmountOnHide={true}
            visible={isVisible}
            animation='slide down' // Transition component smart enough to change to 'slide up' on hide
            duration={200}>
          <Item style={{ paddingLeft: '20px', backgroundColor: 'white' }}>
            <Item.Content>
              {this.opqBoxDetailsList(opqBox)}
            </Item.Content>
          </Item>
        </Transition>
    );

    // Returning an array allows us to return two sibling components (two Items, though one wrapped by Transition)
    return [mainItem, fullBoxDetails];
  }

  getOpqBoxLocationDoc(opqBox) {
    const { locations } = this.props;
    return locations.find(location => opqBox.location === location.slug);
  }

  getOpqBoxLatLngFromZipcode(opqBox) {
    const { zipcodeLatLngDict } = this.props;
    if (opqBox.locations) {
      const zipcode = opqBox.locations[opqBox.locations.length - 1].zipcode;
      const latlng = zipcodeLatLngDict[zipcode];
      console.log(latlng);
      // In rare cases, opqBox will have a zipcode, but its an invalid one and thus not in our zipcodeDict.
      return latlng || [25.0, -71.0];
    }
    return [25.0, -71.0]; // Temporary location for marker if no location information available.
  }

  mapMeasurementsControl() {
    return (
        <Form>
          <Form.Group grouped>
            <label>Measurement Type</label>
            <Form.Field>
              <Checkbox
                  radio
                  label='Voltage'
                  name='measurementTypeRadioGroup'
                  value={this.mapDataDisplayTypes.VOLTAGE_DATA}
                  checked={this.state.currentMapDataDisplay === this.mapDataDisplayTypes.VOLTAGE_DATA}
                  onChange={this.mapMeasurementControlHandleChange.bind(this)}
              />
            </Form.Field>
            <Form.Field>
              <Checkbox
                  radio
                  label='Frequency'
                  name='measurementTypeRadioGroup'
                  value={this.mapDataDisplayTypes.FREQUENCY_DATA}
                  checked={this.state.currentMapDataDisplay === this.mapDataDisplayTypes.FREQUENCY_DATA}
                  onChange={this.mapMeasurementControlHandleChange.bind(this)}
              />
            </Form.Field>
            <Form.Field>
              <Checkbox
                  radio
                  label='THD'
                  name='measurementTypeRadioGroup'
                  value={this.mapDataDisplayTypes.THD_DATA}
                  checked={this.state.currentMapDataDisplay === this.mapDataDisplayTypes.THD_DATA}
                  onChange={this.mapMeasurementControlHandleChange.bind(this)}
              />
            </Form.Field>
          </Form.Group>
          <Form.Group grouped>
            <label>Box Location Granularity</label>
            <Form.Field>
              <Checkbox
                  radio
                  label='Exact Location'
                  name='clusterControlGroup'
                  value={this.mapLocationGranularityTypes.BOX_LOCATION}
                  checked={this.state.currentMapLocationGranularity === this.mapLocationGranularityTypes.BOX_LOCATION}
                  onChange={this.mapLocationGranularityHandleChange.bind(this)}
              />
            </Form.Field>
            <Form.Field>
              <Checkbox
                  radio
                  label='Region'
                  name='clusterControlGroup'
                  value={this.mapLocationGranularityTypes.BOX_REGION}
                  checked={this.state.currentMapLocationGranularity === this.mapLocationGranularityTypes.BOX_REGION}
                  onChange={this.mapLocationGranularityHandleChange.bind(this)}
              />
            </Form.Field>
          </Form.Group>
        </Form>
    );
  }

  mapMeasurementControlHandleChange(event, selectedComponent) {
    const value = selectedComponent.value;
    this.setState({ currentMapDataDisplay: value });
  }

  mapLocationGranularityHandleChange(event, selectedComponent) {
    const value = selectedComponent.value;
    this.setState({ currentMapLocationGranularity: value });
    this.opqBoxLeafletMarkerManagerRefElem.updateMarkerPositions(value);
  }

  setMapRef(elem) {
    // Have to check for elem because this function gets called multiple times during the rendering process,
    // and elem is sometimes undefined.
    if (!this.mapRef && elem) {
      // We store the map height in state so that we can later create the sidePanel div with an equal height.
      // This is needed when we create our map with 100% height, as we don't know the exact height in pixels.
      // Since the sidePanel div is deeply nested within the Map component's Control divs, we can't just simply set
      // the sidePanel div to 100% - we must give it an exact height in pixels.
      const mapHeight = elem.container.clientHeight; // Grab the map's height
      this.mapRef = elem; // Store the Map leaflet ref (not needed in state; just store as instance property)
      this.setState({ mapHeight: mapHeight });
    }
  }

  setOpqBoxLeafletMarkerManagerRef(elem) {
    if (!this.opqBoxLeafletMarkerManagerRefElem && elem) {
      console.log('setting marker manager ref: ', elem);
      this.opqBoxLeafletMarkerManagerRefElem = elem;
    }
  }

  renderPage() {
    const { opqBoxes, locations, regions, zipcodeLatLngDict } = this.props;
    // Initial map center based on arbitrarily chosen OpqBox location. Sidenote: It seems like we're storing location
    // coordinates as [lng, lat] instead of the more traditional [lat, lng]. Intentional?
    const center = this.getOpqBoxLocationDoc(opqBoxes[0]).coordinates.slice().reverse();

    return (
        <WidgetPanel title="Box Map">
          <Map ref={this.setMapRef.bind(this)}
               center={center}
               zoom={11}
               zoomControl={false} // We don't want the default topleft zoomcontrol
               style={{ height: 600 }}>
            <TileLayer
                attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <ZoomControl position='bottomright' />
            <Control position="topright">
              <Popup
                  trigger={<Button color='blue' icon='flask' content='Data Display' />}
                  content={this.mapMeasurementsControl()}
                  on='click'
                  position='bottom right'
              />
            </Control>
            <ScrollableControl position='topleft'>
              {this.sidePanel.bind(this)(this.props.opqBoxes)}
            </ScrollableControl>
            <OpqBoxLeafletMarkerManager
                childRef={this.setOpqBoxLeafletMarkerManagerRef.bind(this)}
                opqBoxes={opqBoxes}
                zipcodeLatLngDict={zipcodeLatLngDict}
                locations={locations}
                regions={regions}
                currentMapDataDisplay={this.state.currentMapDataDisplay}
                mapLocationGranularityTypes={this.mapLocationGranularityTypes}
                mapDataDisplayTypes={this.mapDataDisplayTypes} />
          </Map>
        </WidgetPanel>
    );
  }
}

BoxMap.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
  regions: PropTypes.array.isRequired,
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
  const locationsSub = Meteor.subscribe(Locations.getCollectionName()); // We'll just grab all locations for now.
  const regionsSub = Meteor.subscribe(Regions.getCollectionName()); // Grab all regions as well.
  const currentUser = Meteor.user();
  let opqBoxes = [];
  if (currentUser) {
    const boxIds = BoxOwners.findBoxIdsWithOwner(currentUser.username);
    opqBoxes = OpqBoxes.find({ box_id: { $in: boxIds } }).fetch();
  }

  // Once OpqBoxes subscriptions ready, we make Meteor method calls to retrieve lat-lng from zipcodes for each
  // Region document and OpqBox document that has a locations property.
  // Note: OpqBox.locations might be deprecated now that we have a Locations entity; double check with team.
  if (opqBoxesSub.ready() && boxOwnersSub.ready() && regionsSub.ready() && !methodCallsComplete) {
    // Combine all zipcodes (regions and boxes) that we need to check into a single array for simplicity.
    const boxZipcodes = opqBoxes
                            .filter(opqBox => opqBox.locations && opqBox.locations.length)
                            .map(opqBox => opqBox.locations[opqBox.locations.length - 1].zipcode);

    const regions = Regions.find().fetch();
    // Currently, regionSlug is only storing zipcodes (string), but this might change in the future, so let's
    // ensure we are only dealing with a zipcode here by checking that the string has 5 characters and is numeric.
    const regionZipcodes = regions
                              .filter(region => region.regionSlug && region.regionSlug.length === 5
                                                && !Number.isNaN(region.regionSlug))
                              .map(region => region.regionSlug);

    // Combine zipcodes and filter unique values so we don't perform extra Meteor method calls.
    const combinedZipcodes = [...regionZipcodes, ...boxZipcodes]
                                  .filter((zipcode, idx, arr) => arr.indexOf(zipcode) === idx);

    let numCallsRemaining = combinedZipcodes.length;
    // If no zipcodes to check, mark as complete immediately.
    if (!combinedZipcodes.length) props.setContainerState({ methodCallsComplete: true });
    combinedZipcodes.forEach(zipcode => {
      getZipcodeLatLng.call({ zipcode }, (error, zipcodeDoc) => {
        if (error) console.log(error);
        else {
          const currentZipcodes = zipcodeLatLngDict;
          currentZipcodes[zipcodeDoc.zipcode] = [zipcodeDoc.latitude, zipcodeDoc.longitude];
          props.setContainerState({ zipcodeLatLngDict: currentZipcodes });
        }
        --numCallsRemaining;
        if (numCallsRemaining === 0) props.setContainerState({ methodCallsComplete: true });
      });
    });
  }

  return {
    ready: opqBoxesSub.ready() && boxOwnersSub.ready() && locationsSub.ready() &&
    regionsSub.ready() && methodCallsComplete,
    opqBoxes: opqBoxes,
    locations: Locations.find().fetch(),
    regions: Regions.find().fetch(),
    zipcodeLatLngDict: zipcodeLatLngDict,
  };
};

// Component composition.
export default Lodash.flowRight([
  withStateContainer(containerState),
  withTracker(withTrackerCallback),
])(BoxMap);
