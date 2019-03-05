import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withRouter, Link } from 'react-router-dom';
import { Loader, Button, Icon, Popup, Item, List, Transition, Dropdown, Divider, Label } from 'semantic-ui-react';
import Lodash from 'lodash';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import 'react-leaflet-fullscreen/dist/styles.css';
import FullscreenControl from 'react-leaflet-fullscreen';
import { withTracker } from 'meteor/react-meteor-data';

import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import { Locations } from '../../../api/locations/LocationsCollection';
import { Regions } from '../../../api/regions/RegionsCollection';
import { SystemStats } from '../../../api/system-stats/SystemStatsCollection';
import LeafletMarkerManager from './LeafletMarkerManager';
import ScrollableControl from './ScrollableControl';
import { withContext } from './hocs';
import WidgetPanel from '../../layouts/WidgetPanel';

class BoxMap extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      filteredOpqBoxes: [],
      expandedItemBoxId: '', // Refers to the most recently selected Box in the map side panel listing of boxes.
      mapSidePanelHeight: '600px', // Changes between map fullscreen and regular mode.
    };
  }

  helpText = `
  <p>The Box Map component allows you to view the location of your OPQBoxes on an interactive map.</p>
  <p>The panel on the left side of the map lists all of the OPQBoxes connected to your account. The dropdown box
  at the top of this panel allows you to filter your OPQBoxes based on any given region</p>
  <p>Each OPQBox item in the side panel has a set of buttons that can help you in the following ways:
  <br />
  <b>Zoom to Box</b>: Finds and zooms to this OPQBox on the map.
  <br />
  <b>View Additional Box Details</b>: Display additional information about this OPQBox.
  <br />
  <b>View Box Events</b>: See all PQ events for this OPQBox
  <br />
  <b>View Box Measurements and Trends</b>: See the trends and measurements for this OPQBox.
  </p>
  `;


  /**
   * Marker label, marker popup, and cluster label creation callbacks.
   * To customize the marker, cluster, and popup displays, we define and pass callback functions to the
   * LeafletMarkerManager component as props.
   * See the LeafletMarkerManager PropTypes declaration for more details.
   */

  createMarkerTrendsLabel(locationDoc) {
    const { systemStats, opqBoxes } = this.props;
    const opqBox = opqBoxes.find(box => box.location === locationDoc.slug);
    const latestBoxTrends = systemStats.latest_box_trends;
    const trend = latestBoxTrends.find(boxTrend => boxTrend && boxTrend.box_id === opqBox.box_id);
    const isRecentTrend = (trend && (Date.now() - trend.timestamp_ms) <= 5 * 1000 * 60);
    let trendHtml = '';
    if (trend) {
      trendHtml = `
        <b>${trend.voltage.average.toFixed(2)} V</b>
        <b>${trend.frequency.average.toFixed(3)} Hz</b>
        <b>${trend.thd.average.toFixed(4)} THD</b>
      `;
    }

    return `
        <div>
          <b>${opqBox.name}</b>
          ${isRecentTrend ? trendHtml : '<b>No Recent Data</b>'}
        </div>
    `;
  }

  createMarkerTrendsPopup(locationDoc) {
    const { systemStats, opqBoxes } = this.props;
    const opqBox = opqBoxes.find(box => box.location === locationDoc.slug);
    const latestBoxTrends = systemStats.latest_box_trends;
    const trend = latestBoxTrends.find(boxTrend => boxTrend && boxTrend.box_id === opqBox.box_id);
    const isRecentTrend = (trend && (Date.now() - trend.timestamp_ms) <= 5 * 1000 * 60);
    return (
        <div>
          <b>{opqBox.name}</b><br />
          {isRecentTrend ? (
              <React.Fragment>
                <b>{trend.voltage.average.toFixed(2)} V</b><br />
                <b>{trend.frequency.average.toFixed(3)} Hz</b><br />
                <b>{trend.thd.average.toFixed(4)} THD</b><br />
              </React.Fragment>
          ) : (
            <b>No Recent Data</b>
          )}
        </div>
    );
  }

  createClusterCountLabel(clusterLocationSlugs) {
    const locationCount = clusterLocationSlugs.length;
    return `<div style='font-size: 26px;'><b>${locationCount}</b></div>`;
  }

  createClusterCountSideLabel(clusterLocationSlugs) {
    const locationCount = clusterLocationSlugs.length;
    return `<div><b>Location Count:</b><br />${locationCount}</div>`;
  }

  /**
   * Render Methods
   */

  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active content='Retrieving data...'/>;
  }

  renderPage() {
    const { filteredOpqBoxes } = this.state;
    const { opqBoxes, locations } = this.props;
    const boxes = (filteredOpqBoxes.length) ? filteredOpqBoxes : opqBoxes;
    const boxLocSlugs = boxes.map(box => box.location);
    const filteredLocations = locations.filter(loc => boxLocSlugs.indexOf(loc.slug) > -1);
    // Initial map center based on arbitrarily chosen OpqBox location. Also note that we store coordinates as
    // [lng, lat], but Leaflet requires [lat, lng] - hence the reverse. If no Locations are available, we set the map
    // center to Oahu coordinates by default.
    const boxLocation = this.getOpqBoxLocationDoc(opqBoxes[0]);
    const center = (boxLocation) ? boxLocation.coordinates.slice().reverse() : [21.44, -158.0];
    // It seems that the dropdown menu from the navigation bar has a z-index of 11, which results in the menu clipping
    // beneath the Leaflet map. We set the map's z-index to 10 to fix this.
    const mapStyle = { height: '100%', zIndex: 10 };

    return (
        <WidgetPanel title="Box Map" noPadding={true} helpText={this.helpText}>
          <div style={{ height: '600px' }}>
            <Map ref={this.setMapRef.bind(this)}
                 onResize={this.handleMapOnResize.bind(this)}
                 center={center}
                 zoom={11}
                 zoomControl={false} // We don't want the default topleft zoomcontrol
                 style={mapStyle}>
              <TileLayer
                  attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <ZoomControl position='topright' />
              <FullscreenControl position='topright'/>
              <ScrollableControl position='topleft'>
                {this.renderMapSidePanel(boxes)}
              </ScrollableControl>
              <LeafletMarkerManager
                  locations={filteredLocations}
                  markerLabelFunc={this.createMarkerTrendsLabel.bind(this)}
                  markerPopupFunc={this.createMarkerTrendsPopup.bind(this)}
                  markerClusterLabelFunc={this.createClusterCountLabel.bind(this)}
                  markerClusterSideLabelFunc={this.createClusterCountSideLabel.bind(this)}
                  ref={this.setLeafletMarkerManagerRef.bind(this)} />
            </Map>
          </div>
        </WidgetPanel>
    );
  }

  renderMapSidePanel(opqBoxes) {
    // Side panel height should be equal to Map component height, which can change when map switches between regular
    // and full-screen mode.
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
        {this.renderOpqBoxLegendItemGroup(opqBoxes)}
      </div>
    );
  }

  renderOpqBoxLegendItemGroup(opqBoxes) {
    const opqBoxItems = opqBoxes.map(box => this.renderOpqBoxLegendItem(box));
    return (
        <Item.Group divided style={{ paddingTop: '0px', paddingBottom: '10px' }}>
          {opqBoxItems}
        </Item.Group>
    );
  }

  renderOpqBoxLegendItem(opqBox) {
    const { expandedItemBoxId } = this.state;
    const boxLocationDoc = this.getOpqBoxLocationDoc(opqBox);
    // Using a regular Semantic-UI Link component here triggers the following warning:
    // Warning: Failed context type: The context `router` is marked as required in `Link`, but its value is `undefined`.
    // The reason: The Link component normally inherits the 'router' context by just being a child of the Router
    // component. However, when passed into the Leaflet Map, it loses the 'router' context (managed by React-Router)
    // since the Leaflet Map handles rendering to the DOM separately from React. See:
    // (https://react-leaflet.js.org/docs/en/intro.html#dom-rendering).
    // As a side-note, it seems that React-Router is still utilizing the legacy Context API:
    // (https://reactjs.org/docs/legacy-context.html). However, they also seem to be working to upgrade to the new
    // Context API: (https://github.com/ReactTraining/react-router/pull/5908).

    // We use the withContext() HOC to provide the React Router context to the Link component.
    const LinkWithContext = withContext(Link, this.context);

    const opqBoxItem = (
        <Item style={{ paddingLeft: '20px' }} key={opqBox.box_id}>
          <Item.Content>
            <Item.Header className='mapListingBoxLabel' >{opqBox.name}</Item.Header>
            <Item.Description style={{ marginTop: '0px' }}>
              {boxLocationDoc ? boxLocationDoc.description : 'None'}
            </Item.Description>
            <Item.Description style={{ marginTop: '0px' }}>
              Box ID: {opqBox.box_id}
            </Item.Description>
            <Item.Extra>
              <Button.Group basic size='tiny'>
                <Popup
                    trigger={
                      <Button icon onClick={this.handleZoomButtonClick.bind(this, opqBox.location)}>
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
                      <Button
                          icon
                          as={LinkWithContext}
                          to={{
                            pathname: '/inspector/event',
                            search: `?boxes=${opqBox.box_id}`,
                          }}>
                        <Icon size='large' name='lightning' />
                      </Button>
                    }
                    content='View box events'
                />
                <Popup
                    trigger={
                      <Button
                          icon
                          as={LinkWithContext}
                          to={{
                            pathname: '/livedata',
                            state: { initialBoxIds: [opqBox.box_id] },
                          }}>
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
    const boxDetails = (
        <Transition
            key={`${opqBox.box_id}_details`}
            unmountOnHide={true}
            visible={isVisible}
            animation='slide down' // Transition component smart enough to change to 'slide up' on hide
            duration={200}>
          <Item style={{ paddingLeft: '20px', backgroundColor: 'white' }}>
            <Item.Content>
              {this.renderOpqBoxDetailsList(opqBox)}
            </Item.Content>
          </Item>
        </Transition>
    );

    // Returning an array allows us to return two sibling components (two Items, though one wrapped by Transition)
    return [opqBoxItem, boxDetails];
  }

  renderOpqBoxDetailsList(opqBox) {
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
                <i>{boxLocationDoc ? boxLocationDoc.description : 'None'}</i>
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

  renderRegionDropdown() {
    const { opqBoxes, regions } = this.props;
    // Question: Do we want to list all known regions, or only the ones relevant to the current user's boxes? Going
    // for the latter choice for now.

    // For each OpqBox's location slug, get its region slug.
    // Recall: OpqBox.locationSlug --> Region.locationSlug -> Region.regionSlug
    const opqBoxRegionSlugs = opqBoxes
        .map(box => box.location) // Get box's location slug.
        .map(locSlug => regions.find(region => region && region.locationSlug === locSlug)) // Find location's region doc
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

  /**
   * Event Handlers
   */

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

  handleDetailsButtonClick(opqBox) {
    this.setState({ expandedItemBoxId: opqBox.box_id });
  }

  handleZoomButtonClick(locationSlug) {
    // Since we stored a ref to the LeafletMarkerManager child component, we can call its zoomToMarker method.
    // This is the simplest way to accomplish this task, because the LeafletMarkerManager component maintains
    // the list of Map markers, not this component.
    this.leafletMarkerManagerElem.zoomToMarker(locationSlug);
  }

  handleMapOnResize() {
    const mapHeight = this.mapElem.container.clientHeight;
    this.setState({ mapSidePanelHeight: `${mapHeight}px` });
  }

  /** Helper methods */

  getOpqBoxRegionDoc(opqBox) {
    const { regions } = this.props;
    return regions.find(region => region && region.locationSlug === opqBox.location);
  }

  getOpqBoxLocationDoc(opqBox) {
    const { locations } = this.props;
    if (opqBox && opqBox.location) {
      return locations.find(location => location && location.slug === opqBox.location);
    }
    return null;
  }

  /** Ref Callbacks */

  setMapRef(elem) {
    // Have to check for elem because this function gets called multiple times during the rendering process,
    // and elem is sometimes undefined.
    if (!this.mapElem && elem) {
      this.mapElem = elem; // Store the Map leaflet ref (not needed in state; just store as instance property)
    }
  }

  setLeafletMarkerManagerRef(elem) {
    // Need to store the LeafletMarkerManager child component's ref instance so that we can call its
    // zoomToMarker() method from this component. We just need to set this once.
    if (!this.leafletMarkerManagerElem && elem) {
      this.leafletMarkerManagerElem = elem;
    }
  }
}

BoxMap.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
  regions: PropTypes.array.isRequired,
  systemStats: PropTypes.object,
};

// Required due to DOM conflict between React-Router and Leaflet. See the renderOpqBoxLegendItem() method for
// more details.
BoxMap.contextTypes = {
  router: PropTypes.object.isRequired,
};

// The function that will be passed to the withTracker HOC.
const withTrackerCallback = () => {
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
    opqBoxes = OpqBoxes.find({ box_id: { $in: boxIds } }, { sort: { box_id: 1 } }).fetch();
  }

  return {
    ready: opqBoxesSub.ready() && boxOwnersSub.ready() && locationsSub.ready() &&
    regionsSub.ready() && systemStatsSub.ready(),
    opqBoxes: opqBoxes,
    locations: Locations.find().fetch(),
    regions: Regions.find().fetch(),
    systemStats: SystemStats.findOne(), // Collection should only have 1 actual document.
  };
};

// Component/HOC composition.
export default Lodash.flowRight([
  withTracker(withTrackerCallback),
  withRouter,
])(BoxMap);
