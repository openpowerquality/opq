import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Button, Grid, Segment, List, Checkbox, Popup, Icon } from 'semantic-ui-react';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import OpqBoxLeafletMarkerManager from '../BoxMap/OpqBoxLeafletMarkerManager';
import Moment from 'moment/moment';
import Dygraph from 'dygraphs';
import WidgetPanel from '../../layouts/WidgetPanel';

import { getBoxEvents } from '../../../api/box-events/BoxEventsCollection.methods';
import { getEventData } from '../../../api/fs-files/FSFilesCollection.methods';
import { getEventByEventID } from '../../../api/events/EventsCollection.methods';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../../api/locations/LocationsCollection';

/** Displays event details, including the waveform at the time of the event. */
class EventOverview extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      event: null,
      boxEvents: [],
      boxIdToWaveformDict: {},
    };
  }

  componentDidMount() {
    const { event_id } = this.props;
    // Retrieve relevant Event and BoxEvents for the given event_id.
    this.retrieveInitialData(event_id);
  }

  /**
   * Render Methods
   */

  render() {
    const { event, boxEvents } = this.state;

    // Separate BoxEvents, triggered vs boxes_receveid.
    const triggeredBoxEvents = boxEvents.filter(be => event.boxes_triggered.indexOf(be.box_id) > -1);
    const otherBoxEvents = boxEvents.filter(be => event.boxes_triggered.indexOf(be.box_id) === -1);


    return this.props.ready && !this.state.isLoading ? (
        <Grid container stackable>
          <Grid.Column width={16}>
            <WidgetPanel title='Event Overview'>
              <Grid container>
                <Grid.Column width={12}>{this.eventSummary()}</Grid.Column>
                <Grid.Column width={4}>{this.renderMap()}</Grid.Column>
                <Grid.Column width={16}>
                  <h2>Triggered Boxes</h2>
                  {triggeredBoxEvents.map(boxEvent => (
                      this.boxEventSegment(boxEvent)
                  ))}
                  <h2>Other Boxes</h2>
                  {otherBoxEvents.map(boxEvent => (
                      this.boxEventSegment(boxEvent)
                  ))}
                </Grid.Column>
              </Grid>
            </WidgetPanel>
          </Grid.Column>
        </Grid>
    ) : '';
  }

  renderMap() {
    const { event, boxEvents } = this.state;
    const { opqBoxes, locations } = this.props;

    // Only display on map the OpqBoxes that are relevant to the Event.
    const boxIds = boxEvents.map(be => be.box_id);
    const boxes = opqBoxes.length ? opqBoxes.filter(box => boxIds.indexOf(box.box_id) > -1) : [];

    // It seems that the dropdown menu from the navigation bar has a z-index of 11, which results in the menu clipping
    // beneath the Leaflet map. We set the map's z-index to 10 to fix this.
    const mapStyle = { height: '100%', zIndex: 10 };
    const mapCenter = this.getBoxLocationCoords(event.boxes_triggered[0], opqBoxes, locations) || [21.44, -158.0];

    return boxEvents.length ? (
        <div ref={this.setMapDivRef}
            style={{ height: '300px', width: '100%', boxShadow: '0 1px 2px 0 rgba(34,36,38,.15)',
                      border: '1px solid rgba(34,36,38,.15)' }}>
          <Map center={mapCenter}
               zoom={18}
               zoomControl={false} // We don't want the default topleft zoomcontrol
               style={mapStyle}>
            <TileLayer
                attribution="&amp;copy <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <ZoomControl position='topright' />
            <OpqBoxLeafletMarkerManager
                opqBoxes={boxes}
                locations={locations}
                boxMarkerLabelFunc={this.createBoxMarkerTrendsLabel}
                ref={this.setOpqBoxLeafletMarkerManagerRef} />
          </Map>
        </div>
    ) : '';
  }

  eventSummary() {
    const { event, boxEvents } = this.state;
    const date = event ? Moment(event.target_event_start_timestamp_ms).format('YYYY-MM-DD') : '';
    const time = event ? Moment(event.target_event_start_timestamp_ms).format('HH:mm:ss') : '';
    const duration_ms = event ? event.target_event_end_timestamp_ms - event.target_event_start_timestamp_ms : '';
    let location = '';
    if (event && boxEvents.length) {
      const be = boxEvents.filter(boxEvent => boxEvent.box_id === event.boxes_triggered[0]).shift();
      location = this.getBoxLocationDescription(be.location, be.box_id);
    }

    const pStyle = { fontSize: '16px' };

    return event ? (
      <div>
        <h1>Event Summary</h1>
        <p style={pStyle}>
          An event occurred on <span style={{ backgroundColor: '#b1d4ed' }}>{date} at {time}</span>, lasting for a
          duration of {duration_ms} milliseconds.
        </p>
        <p style={pStyle}>
          The event was initially detected by <span style={{ backgroundColor: '#c3edbb' }}>
          Box {event.boxes_triggered[0]} at {location}</span>, with waveform data available
          for {event.boxes_received.length - 1} other boxes.
        </p>
        <p style={pStyle}>
          The event has been classified as a <span style={{ backgroundColor: '#fcf9a9' }}>{event.type}</span>
        </p>
      </div>
    ) : '';
  }

  boxEventSegment({ event_id, box_id, event_start_timestamp_ms, event_end_timestamp_ms, location }) {
    const { boxIdToWaveformDict } = this.state;
    const waveformVisible = boxIdToWaveformDict[box_id] && boxIdToWaveformDict[box_id].isVisible;
    return (
        <Segment.Group key={box_id}>
          <Segment.Group horizontal>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hdd outline' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Box ID</List.Header>
                    <List.Description><i>{box_id}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hourglass start' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Start Time</List.Header>
                    <List.Description><i>{Moment(event_start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hourglass end' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>End Time</List.Header>
                    <List.Description><i>{Moment(event_end_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='clock' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Duration (ms)</List.Header>
                    <List.Description><i>{event_end_timestamp_ms - event_start_timestamp_ms}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List floated='left'>
                <List.Item>
                  <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Location</List.Header>
                    <List.Description><i>{this.getBoxLocationDescription(location, box_id)}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
              <Popup
                  trigger={
                    <Button icon size='tiny' floated='right' onClick={this.handleZoomButtonClick(box_id)}>
                      <Icon size='large' name='crosshairs' />
                    </Button>
                  }
                  content='Zoom to box location'
              />
            </Segment>
            <Segment>
              <p style={{ marginBottom: '0px' }}><b>Waveform</b></p>
              <Checkbox toggle onClick={this.toggleWaveform(box_id)} />
            </Segment>
          </Segment.Group>
          {waveformVisible &&
          <Segment>
            <div ref={this.setDygraphRef(box_id)} style={{ width: '100%', height: '200px' }}></div>
          </Segment>
          }
        </Segment.Group>
    );
  }

  /**
   * Event Handlers
   */

  toggleWaveform = (box_id) => () => {
    const { boxIdToWaveformDict } = this.state;
    const boxEntry = boxIdToWaveformDict[box_id];

    // Initial toggle will retrieve waveform data.
    if (!boxEntry) {
      // Set visibility to true so that Segment containing dygraph div is rendered. Then retrieve waveform data.
      this.setState(prevState => {
        const dictClone = { ...prevState.boxIdToWaveformDict };
        dictClone[box_id] = { isVisible: true };
        return {
          boxIdToWaveformDict: dictClone,
        };
      }, () => this.retrieveWaveform(box_id));
    } else {
      // Toggle visibility
      this.setState(prevState => {
        const dictClone = { ...prevState.boxIdToWaveformDict };
        dictClone[box_id].isVisible = !dictClone[box_id].isVisible;
        return {
          boxIdToWaveformDict: dictClone,
        };
      }, () => this.createDygraph(this.getDygraphRef(box_id), boxEntry.dyPlotPoints, boxEntry.dyOptions));
    }
  };

  handleZoomButtonClick = box_id => () => {
    this.mapDivElem.scrollIntoView();
    this.opqBoxLeafletMarkerManagerRefElem.zoomToMarker(box_id);
  };

  /**
   * Misc Methods
   */

  retrieveInitialData(event_id) {
    // Given event_id, we'll grab the appropriate Event document, as well as all BoxEvents documents for which data
    // is available (as indicated by Event.boxes_received)
    this.setState({ isLoading: true }, () => {
      getEventByEventID.call({ event_id }, (error, event) => {
        if (error) console.log(error);
        else {
          getBoxEvents.call({ event_id, box_ids: event.boxes_received }, (err, boxEvents) => {
            if (err) console.log(err);
            else {
              this.setState({ boxEvents, event, isLoading: false });
            }
          });
        }
      });
    });
  }

  retrieveWaveform(box_id) {
    const { calibration_constants } = this.props;
    const { boxEvents } = this.state;
    const boxEvent = boxEvents.filter(be => be.box_id === box_id).shift();
    if (!boxEvent) return;

    getEventData.call({ filename: boxEvent.data_fs_filename }, (error, waveform) => {
      if (error) console.log(error);
      else {

        // const dygraphDomElem = this.getDygraphRef(box_id);
        const calibConstant = calibration_constants[box_id] || 1;

        const dyPlotPoints = waveform.map((val, index) => {
          const timestamp = boxEvent.event_start_timestamp_ms + (index * (1.0 / 12.0));
          return [timestamp, val / calibConstant];
        });
        const dyOptions = {
          labels: ['Timestamp', 'Voltage'],
          axes: {
            x: {
              valueFormatter: (millis, opts, seriesName, dygraph, row, col) => { // eslint-disable-line no-unused-vars
                // We must separately calculate the microseconds and concatenate it to the date string.
                const dateString = Moment(millis).format('[[]MM-DD-YYYY[]] HH:mm:ss.SSS').toString()
                    + ((row * (1.0 / 12.0)) % 1).toFixed(3).substring(2);
                return dateString;
              },
              axisLabelFormatter: (timestamp) => Moment(timestamp).format('HH:mm:ss.SSS'),
              pixelsPerLabel: 80,
            },
          },
        };

        this.createDygraph(this.getDygraphRef(box_id), dyPlotPoints, dyOptions);

        // Store plot points and options for the given box_id.
        this.setState(prevState => {
          const updatedDict = { ...prevState.boxIdToWaveformDict };
          updatedDict[box_id] = { ...updatedDict[box_id], dyPlotPoints, dyOptions };
          return {
            boxIdToWaveformDict: updatedDict,
          };
        });
      }
    });
  }

  getBoxLocationDoc(box_id, opqBoxes, locations) {
    const opqBox = opqBoxes.filter(box => box.box_id === box_id).shift();
    if (opqBox) {
      const loc = locations.find(location => location && location.slug === opqBox.location);
      return loc;
      // return loc ? loc.coordinates.slice().reverse() : null;
    }
    return null;
  }

  getBoxLocationDescription(locationSlug, box_id) {
    const { locations, opqBoxes } = this.props;

    // LocationSlug should be a string. However, there is a bug in which BoxEvents.location is sometimes an array of
    // (incorrect) historic location data. In these cases, we will simply retrieve the box's current location. Once
    // Makai fixes this bug, we should probably remove this conditional.
    if (typeof locationSlug !== 'string') {
      const opqBox = opqBoxes.filter(box => box.box_id === box_id).shift();
      if (opqBox) {
        const location = locations.filter(loc => loc.slug === opqBox.location).shift();
        return location ? location.description : null;
      }
    }

    const location = locations.filter(loc => loc.slug === locationSlug).shift();
    return location ? location.description : null;
  }

  getBoxLocationCoords(box_id, opqBoxes, locations) {
    const location = this.getBoxLocationDoc(box_id, opqBoxes, locations);
    return location ? location.coordinates.slice().reverse() : null;

    // const opqBox = opqBoxes.filter(box => box.box_id === box_id).shift();
    // if (opqBox) {
    //   const loc = locations.find(location => location && location.slug === opqBox.location);
    //   return loc ? loc.coordinates.slice().reverse() : null;
    // }
    // return null;
  }

  createDygraph(dyDomElement, dyPlotPoints, dyPlotOptions) {
    // Note: There's no real need to store the Dygraph instance itself. It's simpler to allow render() to create a new
    // instance each time the graph visibility is set to true.
    return new Dygraph(dyDomElement, dyPlotPoints, dyPlotOptions);
  }

  createBoxMarkerTrendsLabel(opqBoxDoc) {
    return `
      <div>
        <b>${opqBoxDoc.name}</b>
        <b>Box ID ${opqBoxDoc.box_id}</b>
      </div>
    `;
  }

  /**
   * Ref methods
   * Interacting with non-React third party DOM libraries (such as Dygraph) requires the usage of React Refs.
   * Read more here: https://reactjs.org/docs/refs-and-the-dom.html
   */

  setDygraphRef = box_id => elem => {
    if (elem) this[`dygraph_box_id_${box_id}`] = elem;
  };

  getDygraphRef = box_id => this[`dygraph_box_id_${box_id}`];

  setOpqBoxLeafletMarkerManagerRef = elem => {
    // Need to store the OpqBoxLeafletMarkerManager child component's ref instance so that we can call its
    // zoomToMarker() method from this component.
    if (elem) {
      this.opqBoxLeafletMarkerManagerRefElem = elem;
    }
  };

  setMapDivRef = elem => {
    if (elem) this.mapDivElem = elem;
  };
}

EventOverview.propTypes = {
  ready: PropTypes.bool.isRequired,
  event_id: PropTypes.number.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
  calibration_constants: PropTypes.object.isRequired,
};

export default withTracker((props) => {
  const locationsSub = Meteor.subscribe(Locations.getCollectionName());
  const opqBoxesSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  const opqBoxes = OpqBoxes.find().fetch();

  return {
    ready: opqBoxesSub.ready() && locationsSub.ready(),
    event_id: Number(props.match.params.event_id),
    opqBoxes,
    locations: Locations.find().fetch(),
    calibration_constants: opqBoxes.length ? Object.assign(...OpqBoxes.find().fetch().map(box => (
                            { [box.box_id]: box.calibration_constant }
                        ))) : {},
  };
})(EventOverview);
