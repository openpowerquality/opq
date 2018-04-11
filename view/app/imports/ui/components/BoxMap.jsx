import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { ReactiveVar } from 'meteor/reactive-var';
import { List, Loader } from 'semantic-ui-react';
import { Map, TileLayer, Marker, Popup, LayerGroup, LayersControl, FeatureGroup, Circle, Rectangle } from 'react-leaflet';
import 'semantic-ui-css/semantic.css';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { BoxOwners } from '../../api/users/BoxOwnersCollection';
import { getZipcodeLatLng } from '../../api/zipcodes/ZipcodesCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';

const { BaseLayer, Overlay } = LayersControl;

/** Display system statistics. */
class BoxMap extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      locations: {},
    };
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active content='Retrieving data...'/>;
  }

  opqBoxCircles() {
    const circles = this.props.opqBoxes.map(opqBox => (
      <Circle
          key={opqBox._id}
          // Bermuda triangle coords when unknown zipcode, until we find a better way to handle it. Teehee...
          center={this.props.zipcodeLatLngDict[opqBox.locations[opqBox.locations.length - 1].zipcode] || [25.0, -71.0]}
          radius={3000}>
        <Popup>
          {this.popupContents(opqBox)}
        </Popup>
        <Marker key={opqBox._id} position={this.props.zipcodeLatLngDict[opqBox.locations[opqBox.locations.length - 1].zipcode] || [25.0, -71.0] }>
          <Popup>
            {this.popupContents(opqBox)}
          </Popup>
        </Marker>
      </Circle>
    ));
    return circles;
  }

  popupContents(opqBox) {
    return (
        <List>
          <List.Item>
            <List.Icon name='disk outline' />
            <List.Content>Name: {opqBox.name}</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='marker' />
            <List.Content>Location: {opqBox.locations[opqBox.locations.length - 1].zipcode.toString()}</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='tag' />
            <List.Content>Description: {opqBox.description}</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name='plug' />
            <List.Content>Unplugged Status: {opqBox.unplugged.toString()}</List.Content>
          </List.Item>
        </List>
    );
  }

  renderPage() {
    const firstZipcode = Object.keys(this.props.zipcodeLatLngDict).reverse()[0]; // Reverse so Hawaii zipcodes first.
    const center = (firstZipcode) ? this.props.zipcodeLatLngDict[firstZipcode] : [21.31, -157.86]; // Default to Oahu.

    return (
        <WidgetPanel title="Box Map">
          <Map center={center} zoom={11} style={{ height: 600 }}>
            <LayersControl position="topright">
              <BaseLayer checked name="OpenStreetMap.Mapnik">
                <TileLayer
                    attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
              </BaseLayer>
              <BaseLayer name="OpenStreetMap.BlackAndWhite">
                <TileLayer
                    attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                    url="https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png"
                />
              </BaseLayer>
              <Overlay checked name="Marker with popup">
                <LayerGroup>
                  {this.opqBoxCircles()}
                </LayerGroup>
              </Overlay>
            </LayersControl>
          </Map>
        </WidgetPanel>
    );
  }
}

/** Require an array of Stuff documents in the props. */
BoxMap.propTypes = {
  ready: PropTypes.bool.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  zipcodeLatLngDict: PropTypes.object.isRequired,
};

// (Experimental) Need this ReactiveVar outside the computation in order to be able to detect and finish all
// Meteor method calls in withTracker() before passing props down to the component. This is almost certainly
// the wrong way of doing things, but it works for now until I figure out how to properly use Meteor methods calls with
// React's lifecycle methods.
const methodCallsComplete = new ReactiveVar(false);
const zipcodeLatLngDict = {};
/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Even though this subscription correctly retrieves only the currently logged in user's boxes, remember that
  // Minimongo merges any other OpqBox documents from other OpqBox subscriptions (even from other currently rendered
  // React components!) into the same client side collection.
  // Therefore, it's not always enough to simply subscribe to a publication - we sometimes have to follow it up with
  // another Mongo query on the client side to make sure we are working with the correct subset of documents.

  // While it might seem strange to be subscribing to the BoxOwners collection here, especially since the
  // GET_CURRENT_USER_OPQ_BOXES subscription correctly only returns the current user's opq boxes - because of the
  // problems described above about Minimongo, we must be sure to filter out OpqBox documents that might exist
  // in the client side collection that do not belong to the currently logged in user.
  // There are two approaches:
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

  if (opqBoxesSub.ready() && boxOwnersSub.ready() && !methodCallsComplete.get()) {
    let numCallsRemaining = opqBoxes.length;
    if (opqBoxes.length === 0) methodCallsComplete.set(true); // If no boxes for user, can skip this entirely.
    opqBoxes.forEach(box => {
      const zipcode = box.locations[box.locations.length - 1].zipcode;
      getZipcodeLatLng.call({ zipcode }, (error, zipcodeDoc) => {
        --numCallsRemaining;
        if (error) console.log(error);
        else {
          // console.log('zipcode meteor call result: ', zipcodeDoc);
          zipcodeLatLngDict[zipcodeDoc.zipcode] = [zipcodeDoc.latitude, zipcodeDoc.longitude];
          if (numCallsRemaining === 0) methodCallsComplete.set(true);
        }
      });
    });
  }

  return {
    ready: opqBoxesSub.ready() && boxOwnersSub.ready() && methodCallsComplete.get(),
    opqBoxes: opqBoxes,
    zipcodeLatLngDict,
  };
})(BoxMap);

