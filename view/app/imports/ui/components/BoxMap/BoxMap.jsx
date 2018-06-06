import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withRouter } from 'react-router-dom';
import { Loader, Form, Checkbox, Button, Icon, Popup, Item, List,
          Transition, Dropdown, Divider, Label } from 'semantic-ui-react';
// import 'semantic-ui-css/semantic.css';
import Lodash from 'lodash';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import Control from 'react-leaflet-control';
import 'react-leaflet-fullscreen/dist/styles.css';
import FullscreenControl from 'react-leaflet-fullscreen';
import { withTracker } from 'meteor/react-meteor-data';
import { withStateContainer } from './hocs';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import { Locations } from '../../../api/locations/LocationsCollection';
import { Regions } from '../../../api/regions/RegionsCollection';
import { SystemStats } from '../../../api/system-stats/SystemStatsCollection';
import { getZipcodeLatLng } from '../../../api/zipcodes/ZipcodesCollectionMethods';
import OpqBoxLeafletMarkerManager from './OpqBoxLeafletMarkerManager';
import ScrollableControl from './ScrollableControl';

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
      filteredOpqBoxes: [],
      currentMapDataDisplay: this.mapDataDisplayTypes.VOLTAGE_DATA,
      currentMapLocationGranularity: this.mapLocationGranularityTypes.BOX_LOCATION,
      expandedItemBoxId: '', // Refers to the most recently selected Box in the map side panel listing of boxes.
      mapSidePanelHeight: '600px', // Changes between map fullscreen and regular mode.
      showDataDisplayButtonContents: false,
    };
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active content='Retrieving data...'/>;
  }

  createBoxMarkerTrendsLabel(opqBoxDoc) {
    const { systemStats } = this.props;
    const latestBoxTrends = systemStats.latest_box_trends;
    const trend = latestBoxTrends.find(boxTrend => boxTrend.box_id === opqBoxDoc.box_id);
    const isRecentTrend = (trend && (Date.now() - trend.timestamp_ms) <= 5 * 1000 * 60);
    let trendHtml = '';
    if (trend) {
      trendHtml = `
        <b>${trend.voltage.average.toFixed(2)} V</b>
        <b>${trend.frequency.average.toFixed(3)} F</b>
        <b>${trend.thd.average.toFixed(4)} THD</b>
      `;
    }

    const markerHtml = `
        <div>
          <b>${opqBoxDoc.name}</b>
          ${isRecentTrend ? trendHtml : '<b>No Recent Data</b>'}
        </div>`;
    return markerHtml;
  }

  createClusterBoxCountLabel(clusterBoxIds) {
    const boxCount = clusterBoxIds.length;
    return `<div style='font-size: 26px;'><b>${boxCount}</b></div>`;
  }

  createClusterBoxCountSideLabel(clusterBoxIds) {
    const boxCount = clusterBoxIds.length;
    return `<div><b>Box Count:</b><br />${boxCount}</div>`;
  }

  sidePanel(opqBoxes) {
    // Side panel height should be equal to Map component height.
    const { mapSidePanelHeight } = this.state;
    return (
      <div
          className='mapListShadow'
          style={{ height: mapSidePanelHeight, width: '300px', marginLeft: '-10px', marginTop: '-10px',
                  overflow: 'auto', backgroundColor: '#f9f9f9' }}>

        <div style={{ paddingLeft: '10px', paddingRight: '10px', marginTop: '10px', width: '100%' }}>
          <Label style={{ marginBottom: '5px' }}>
            <Icon name='filter'></Icon>Filter by Region
          </Label>
          {this.renderRegionDropdown()}
        </div>
        <Divider />
        {this.opqBoxItemGroup(opqBoxes)}
      </div>
    );
  }

  renderRegionDropdown() {
    const { opqBoxes, regions } = this.props;
    // Question: Do we want to list all known regions, or only the ones relevant to the current user's boxes? Going
    // for the latter choice for now.

    // For each OpqBox's location slug, get its region slug.
    // Recall: OpqBox.locationSlug --> Region.locationSlug -> Region.regionSlug
    const opqBoxRegionSlugs = opqBoxes
        .map(box => box.location) // Get box's location slug.
        .map(locSlug => regions.find(region => region.locationSlug === locSlug)) // Find location's region doc.
        .filter(regionDoc => regionDoc) // Removes any undefined results from above map.
        .map(regionDoc => regionDoc.regionSlug) // Grab the Region's slug.
        .filter((slug, idx, arr) => arr.indexOf(slug) === idx); // Filter for unique values.

    const dropdownOptions = opqBoxRegionSlugs.map(slug => ({ key: slug, value: slug, text: slug }));

    return <Dropdown placeholder='Region Filter'
                     fluid={true}
                     multiple={true}
                     openOnFocus={false}
                     selectOnBlur={false}
                     selectOnNavigation={false}
                     selection
                     options={dropdownOptions}
                     onChange={this.handleRegionDropdownOnChange.bind(this)} />;
  }

  handleRegionDropdownOnChange(event, data) {
    const { regions, opqBoxes } = this.props;

    const selectedRegions = data.value; // Given to us as an array.

    // Find all boxIds associated with the selected list of regions.
    // First, get locationSlug of each regionSlug
    const locSlugs = regions
        .filter(reg => selectedRegions.includes(reg.regionSlug))
        .map(reg => reg.locationSlug);

    // Then filter boxes and update state.
    const filteredOpqBoxes = opqBoxes.filter(box => locSlugs.includes(box.location));
    this.setState({ filteredOpqBoxes: filteredOpqBoxes });
  }

  opqBoxItemGroup(opqBoxes) {
    const opqBoxItems = opqBoxes.map(box => this.opqBoxItem(box));
    return (
        <Item.Group divided style={{ paddingTop: '0px', paddingBottom: '10px' }}>
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

  getOpqBoxRegionDoc(opqBox) {
    const { regions } = this.props;
    return regions.find(region => region.locationSlug === opqBox.location);
  }

  opqBoxDetailsList(opqBox) {
    const boxLocationDoc = this.getOpqBoxLocationDoc(opqBox);
    const boxRegionDoc = this.getOpqBoxRegionDoc(opqBox);
    return (
        <List divided style={{ width: '250px' }}>
          <List.Item>
            <List.Icon name='hdd outline' color='blue' size='large' verticalAlign='middle' />
            <List.Content style={{ paddingLeft: '2px' }}>
              <List.Header>Box Name</List.Header>
              <List.Description><i>{opqBox.name}</i></List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='hashtag' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header>Box ID</List.Header>
              <List.Description><i>{opqBox.box_id}</i></List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header>Location</List.Header>
              <List.Description>
                <i>{boxLocationDoc ? (boxLocationDoc.description) : ('None')}</i>
              </List.Description>
              <List.Header>Coordinates</List.Header>
              <List.Description>
                <i>{boxLocationDoc
                    ? (`Lat: ${boxLocationDoc.coordinates[1]}, Lng: ${boxLocationDoc.coordinates[0]}`)
                    : ('None')}
                </i>
              </List.Description>
              <List.Header><i>Region</i></List.Header>
              <List.Description>
                {boxRegionDoc ? (<i>{boxRegionDoc.regionSlug}</i>) : ('None')}
              </List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='tag' color='blue' size='large' verticalAlign='middle' />
            <List.Content style={{ paddingLeft: '4px' }}>
              <List.Header><i>Description</i></List.Header>
              <List.Description><i>{opqBox.description}</i></List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='plug' color='blue' size='large' verticalAlign='middle' />
            <List.Content>
              <List.Header><i>Unplugged Status</i></List.Header>
              <List.Description><i>{opqBox.unplugged.toString()}</i></List.Description>
            </List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='creative commons' color='blue' size='large' verticalAlign='middle' />
            <List.Content style={{ paddingLeft: '4px' }}>
              <List.Header>Calibration Constant</List.Header>
              <List.Description><i>{opqBox.calibration_constant}</i></List.Description>
            </List.Content>
          </List.Item>
        </List>
    );
  }

  handleBoxSettingsButtonOnClick(opqBox) {
    // eslint-disable-next-line react/prop-types
    this.props.history.push(`/edit/${opqBox.box_id}`);
  }

  handleBoxEventsButtonOnClick() {
    // eslint-disable-next-line react/prop-types
    this.props.history.push('/inspector');
  }

  handleBoxMeasurementsTrendsButtonOnClick() {
    // eslint-disable-next-line react/prop-types
    this.props.history.push('/livedata');
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
                      <Button icon onClick={this.handleBoxSettingsButtonOnClick.bind(this, opqBox)}>
                        <Icon size='large' name='setting' />
                      </Button>
                    }
                    content='Box Settings'
                />
                <Popup
                    trigger={
                      <Button icon onClick={this.handleBoxEventsButtonOnClick.bind(this)}>
                        <Icon size='large' name='lightning' />
                      </Button>
                    }
                    content='View box events'
                />
                <Popup
                    trigger={
                      <Button icon onClick={this.handleBoxMeasurementsTrendsButtonOnClick.bind(this)}>
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
  }

  setMapRef(elem) {
    // Have to check for elem because this function gets called multiple times during the rendering process,
    // and elem is sometimes undefined.
    if (!this.mapRef && elem) {
      this.mapRef = elem; // Store the Map leaflet ref (not needed in state; just store as instance property)
    }
  }

  setOpqBoxLeafletMarkerManagerRef(elem) {
    // Need to store the OpqBoxLeafletMarkerManager child component's ref instance so that we can call its
    // zoomToMarker() method from this component. We just need to set this once.
    if (!this.opqBoxLeafletMarkerManagerRefElem && elem) {
      this.opqBoxLeafletMarkerManagerRefElem = elem;
    }
  }

  handleMapOnClick() {
    // Close Data Display button whenever map is clicked. This is a simple workaround for not being able to
    // close the data display button onBlur, which what we actually want.
    this.setState({ showDataDisplayButtonContents: false });
  }

  handleMapOnResize() {
    const mapHeight = this.mapRef.container.clientHeight;
    this.setState({ mapSidePanelHeight: `${mapHeight}px` });
  }

  handleDataDisplayButtonClick() {
    this.setState((prevState) => ({ showDataDisplayButtonContents: !prevState.showDataDisplayButtonContents }));
  }

  mapDataDisplayButton() {
    const { showDataDisplayButtonContents } = this.state;
    // Previously, we were simply using a Semantic-UI Popup component. However, it had problems displaying the popup
    // contents while the map was in full screen mode. It turns out the reason for this was because the Popup component
    // utilizes React's Portal mechanism, in which the popup contents are placed elsewhere in the DOM away from where
    // the Popup component is created. The react-leaflet-fullscreen component will only display contents that are a
    // child of the Map component. Since the Popup content's are placed in a Portal outside of the map component, they
    // were not rendering properly.
    // Fortunately, it's simple enough to create a basic popup ourselves, utilizing a single state boolean variable
    // to tell us whether the button contents should be hidden or shown.
    return (
        <div>
          <Button onClick={this.handleDataDisplayButtonClick.bind(this)}
                  color='blue'
                  icon='flask'
                  content='Data Display'
                  style={{ float: 'right' }} />
          {showDataDisplayButtonContents &&
            <Label onBlur={() => console.log('blurred')}
                   pointing='above'
                   style={{ backgroundColor: 'white', fontWeight: 'normal', padding: '15px',
                            float: 'right', clear: 'both' }}>
              {this.mapMeasurementsControl()}
            </Label>
          }
        </div>
    );
  }

  renderPage() {
    const { filteredOpqBoxes } = this.state;
    const { opqBoxes, locations, regions, zipcodeLatLngDict } = this.props;
    const boxes = (filteredOpqBoxes.length) ? filteredOpqBoxes : opqBoxes;
    // Initial map center based on arbitrarily chosen OpqBox location. Sidenote: It seems like we're storing location
    // coordinates as [lng, lat] instead of the more traditional [lat, lng]. Intentional?
    const center = this.getOpqBoxLocationDoc(opqBoxes[0]).coordinates.slice().reverse();

    return (
        <div style={{ height: '600px' }}>
          <Map ref={this.setMapRef.bind(this)}
               onClick={this.handleMapOnClick.bind(this)}
               onResize={this.handleMapOnResize.bind(this)}
               center={center}
               zoom={11}
               zoomControl={false} // We don't want the default topleft zoomcontrol
               style={{ height: '100%' }}>
            <TileLayer
                attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <ZoomControl position='bottomright' />
            <FullscreenControl position='bottomright'/>
            <Control position="topright">
              {this.mapDataDisplayButton()}
            </Control>
            <ScrollableControl position='topleft'>
              {this.sidePanel.bind(this)(boxes)}
            </ScrollableControl>
            <OpqBoxLeafletMarkerManager
                childRef={this.setOpqBoxLeafletMarkerManagerRef.bind(this)}
                opqBoxes={boxes}
                boxMarkerLabelFunc={this.createBoxMarkerTrendsLabel.bind(this)}
                markerClusterLabelFunc={this.createClusterBoxCountLabel.bind(this)}
                markerClusterSideLabelFunc={this.createClusterBoxCountSideLabel.bind(this)}
                zipcodeLatLngDict={zipcodeLatLngDict}
                locations={locations}
                regions={regions}
                currentMapDataDisplay={this.state.currentMapDataDisplay}
                currentMapLocationGranularity={this.state.currentMapLocationGranularity}
                mapLocationGranularityTypes={this.mapLocationGranularityTypes}
                mapDataDisplayTypes={this.mapDataDisplayTypes} />
          </Map>
        </div>
    );
  }
}

BoxMap.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
  regions: PropTypes.array.isRequired,
  zipcodeLatLngDict: PropTypes.object.isRequired,
  systemStats: PropTypes.object,
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
  const systemStatsSub = Meteor.subscribe(SystemStats.getCollectionName());
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
    regionsSub.ready() && systemStatsSub.ready() && methodCallsComplete,
    opqBoxes: opqBoxes,
    locations: Locations.find().fetch(),
    regions: Regions.find().fetch(),
    zipcodeLatLngDict: zipcodeLatLngDict,
    systemStats: SystemStats.findOne(), // Collection should only have 1 actual document.
  };
};

// Component composition.
export default Lodash.flowRight([
  withStateContainer(containerState),
  withTracker(withTrackerCallback),
  withRouter,
])(BoxMap);
