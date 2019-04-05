import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Link } from 'react-router-dom';
import { Grid, Loader, Message, Icon, Button } from 'semantic-ui-react';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import Moment from 'moment/moment';
import LeafletMarkerManager from '../BoxMap/LeafletMarkerManager';

import WidgetPanel from '../../layouts/WidgetPanel';
import BoxEventSummary from './BoxEventSummary';

import { getBoxEvents } from '../../../api/box-events/BoxEventsCollection.methods';
import { getEventByEventID } from '../../../api/events/EventsCollection.methods';
import { getIncidentsFromEventID } from '../../../api/incidents/IncidentsCollection.methods';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../../api/locations/LocationsCollection';


/** Displays event details, including the waveform at the time of the event. */
class EventViewer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      event: null,
      boxEvents: [],
      derivedIncidents: [],
      errorReason: null,
    };
  }

  componentDidMount() {
    const { event_id } = this.props;
    // Retrieve relevant Event and BoxEvents for the given event_id.
    this.retrieveInitialData(event_id);
  }

  helpText = `
  <p>The Event Overview panel displays the details of an event, including waveform data collected from individual
  boxes during the time of the event.</p>
  <p>To view a box's waveform, simply click the "Waveform" toggle button. Note that it might take up to a few seconds to
  download and display the waveform, especially for longer duration events.</p>
  <p>The map displays the locations of all relevant OPQ Boxes during the time of the event. It is initially zoomed in on
  the OPQ Box that first detected the event.</p>
  `;

  /**
   * Render Methods
   */

  render() {
    if (this.state.errorReason) return this.renderError(this.state.errorReason);
    return (this.props.ready && !this.state.isLoading) ? this.renderPage() : <Loader active content='Loading...'/>;
  }

  renderPage() {
    const { event, boxEvents } = this.state;
    const { triggeredBoxEvents, otherBoxEvents } = this.separateBoxEvents(event, boxEvents);

    return (
        <Grid container stackable>
          <Grid.Column width={16}>
            <WidgetPanel title='Event Viewer' helpText={this.helpText}>
              <Grid container>
                <Grid.Column width={12}>{this.renderEventSummary()}</Grid.Column>
                <Grid.Column width={4}>{this.renderMap()}</Grid.Column>
                <Grid.Column width={16}>
                  <h2>Triggered Boxes</h2>
                  {triggeredBoxEvents.map(boxEvent => (
                      <BoxEventSummary key={boxEvent.box_id}
                                       boxEventDoc={boxEvent}
                                       locationDoc={this.getBoxEventLocationDoc(boxEvent)}
                                       calibrationConstant={this.getBoxCalibrationConstant(boxEvent.box_id)}
                                       mapZoomCallback={this.handleZoomButtonClick} />
                  ))}
                  {otherBoxEvents.length ? <h2>Other Boxes</h2> : null}
                  {otherBoxEvents.map(boxEvent => (
                      <BoxEventSummary key={boxEvent.box_id}
                                       boxEventDoc={boxEvent}
                                       locationDoc={this.getBoxEventLocationDoc(boxEvent)}
                                       calibrationConstant={this.getBoxCalibrationConstant(boxEvent.box_id)}
                                       mapZoomCallback={this.handleZoomButtonClick} />
                  ))}
                </Grid.Column>
              </Grid>
            </WidgetPanel>
          </Grid.Column>
        </Grid>
    );
  }

  renderMap() {
    const { event, boxEvents } = this.state;
    const { locations } = this.props;

    // Only display on map the Locations that are relevant to the Event.
    const boxEventLocationSlugs = boxEvents.map(be => be.location);
    const filteredLocations = locations.filter(loc => boxEventLocationSlugs.indexOf(loc.slug) > -1);

    // Center the map on the initial triggering box event location. In the rare case that it is not available, we choose
    // an arbitrary box event from boxes_received instead.
    const { triggeredBoxEvents, otherBoxEvents } = this.separateBoxEvents(event, boxEvents);
    const boxEvent = (triggeredBoxEvents.length) ? triggeredBoxEvents[0] : otherBoxEvents[0];
    const boxEventLocation = this.getBoxEventLocationDoc(boxEvent);
    const mapCenter = this.getLocationCoords(boxEventLocation);

    // It seems that the dropdown menu from the navigation bar has a z-index of 11, which results in the menu clipping
    // beneath the Leaflet map. We set the map's z-index to 10 to fix this.
    const mapStyle = { height: '100%', zIndex: 10 };

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
            <LeafletMarkerManager
                locations={filteredLocations}
                markerLabelFunc={this.createMarkerLabel}
                ref={this.setLeafletMarkerManagerRef} />
          </Map>
        </div>
    ) : '';
  }

  renderEventSummary() {
    const { event, boxEvents, derivedIncidents } = this.state;
    const date = event ? Moment(event.target_event_start_timestamp_ms).format('YYYY-MM-DD') : '';
    const time = event ? Moment(event.target_event_start_timestamp_ms).format('HH:mm:ss') : '';
    const duration_ms = event ? event.target_event_end_timestamp_ms - event.target_event_start_timestamp_ms : '';

    // Get the location description of the initial triggered box event.
    const { triggeredBoxEvents } = this.separateBoxEvents(event, boxEvents);
    const boxEvent = (triggeredBoxEvents.length) ? triggeredBoxEvents[0] : null;
    const locationDoc = boxEvent ? this.getBoxEventLocationDoc(boxEvent) : null;
    const triggeredBoxEventLocation = locationDoc ? locationDoc.description : 'UNAVAILABLE';

    const pStyle = { fontSize: '16px' };

    const derivedIncidentsDisplay = derivedIncidents.length ? (
        <div>
          <p style={pStyle}>
            This event generated {derivedIncidents.length} incidents:
          </p>
          <div style={{ marginTop: '5px' }}>
            {derivedIncidents.map(inci => this.renderButtonLink({
              key: inci.incident_id,
              to: `/inspector/incident/${inci.incident_id}`,
              text: `Incident #${inci.incident_id}`,
            }))}
          </div>
        </div>
    ) : (
        <p style={pStyle}>
          This event did not generate any Incidents
        </p>
    );

    return event ? (
      <div>
        <h1>Event Summary (#{event.event_id})</h1>
        <p style={pStyle}>
          An event occurred on <span style={{ backgroundColor: '#b1d4ed' }}>{date} at {time}</span>, lasting for a
          duration of {duration_ms} milliseconds.
        </p>
        <p style={pStyle}>
          The event was initially detected by <span style={{ backgroundColor: '#c3edbb' }}>
          Box {event.boxes_triggered[0]} at {triggeredBoxEventLocation}</span>, with waveform data available
          for {event.boxes_received.filter(box_id => box_id !== event.boxes_triggered[0]).length} other boxes.
        </p>
        {derivedIncidentsDisplay}
      </div>
    ) : '';
  }

  renderButtonLink({ key = null, to, text, color = 'green' }) {
    return (
        <Button
            key={key}
            style={{ marginBottom: '3px' }}
            icon
            color={color}
            as={Link}
            to={to}>
          <Icon size='large' name='share' />
          <span style={{ marginLeft: '3px', verticalAlign: 'middle' }}>{text}</span>
        </Button>
    );
  }

  renderError(errorMessage) {
    return (
        <Grid centered container stackable>
          <Grid.Column width={6}>
            <Message icon negative>
              <Icon name='exclamation' />
              <Message.Content>
                <Message.Header>Oops! Looks like something went wrong.</Message.Header>
                <p>{errorMessage}</p>
              </Message.Content>
            </Message>
          </Grid.Column>
        </Grid>
    );
  }

  /**
   * Event Handlers
   */

  handleZoomButtonClick = locationSlug => () => {
    this.getMapDivRef().scrollIntoView();
    this.getLeafletMarkerManagerRef().zoomToMarker(locationSlug);
  };

  createMarkerLabel = (locationDoc) => {
    const { event, boxEvents } = this.state;
    const { triggeredBoxEvents, otherBoxEvents } = this.separateBoxEvents(event, boxEvents);
    const boxEvent = (triggeredBoxEvents.length) ? triggeredBoxEvents[0] : otherBoxEvents[0];
    const boxIdStr = boxEvent && boxEvent.box_id ? `<b>Box ID ${boxEvent.box_id}</b>` : '';
    return `
      <div>
        <b>${locationDoc.description}</b>
        ${boxIdStr}
      </div>
    `;
  };

  /**
   * Helper/Misc Methods
   */

  retrieveInitialData(event_id) {
    // Given event_id, we'll grab the appropriate Event document, as well as all BoxEvents documents for which data
    // is available (as indicated by Event.boxes_received)
    this.setState({ isLoading: true }, () => {
      getEventByEventID.call({ event_id }, (error, event) => {
        if (error) {
          console.log(error);
          if (error.error === 'invalid-event-id') {
            this.setState({ isLoading: false, errorReason: error.reason });
          }
        } else {
          getBoxEvents.call({ event_id, box_ids: event.boxes_received }, (err, boxEvents) => {
            if (err) {
              console.log(err);
              if (err.error === 'no-box-events-found') {
                this.setState({ isLoading: false, errorReason: err.reason });
              }
            } else {
              const fixedBoxEvents = boxEvents.map(be => this.ensureBoxEventLocationSlug(be));
              this.setState({ boxEvents: fixedBoxEvents, event, isLoading: false });
            }
          });
        }
      });
    });

    // Retrieve any derived Incidents. Note: No need to set isLoading for this, just do it in the background.
    getIncidentsFromEventID.call({ event_id }, (error, incidents) => {
      if (error) console.log(error);
      else {
        this.setState({ derivedIncidents: incidents });
      }
    });
  }


  getBoxCalibrationConstant(box_id) {
    const { opqBoxes } = this.props;
    const opqBox = opqBoxes.find(box => box.box_id === box_id);
    return opqBox ? opqBox.calibration_constant : 1;
  }

  getBoxEventLocationDoc(boxEvent) {
    const { locations } = this.props;
    return locations.find(loc => loc.slug === boxEvent.location);
  }

  getLocationCoords(location) {
    return location ? location.coordinates.slice().reverse() : null;
  }

  separateBoxEvents(event, boxEvents) {
    const triggeredBoxEvents = [];
    const otherBoxEvents = [];

    boxEvents.forEach(be => {
      if (event.boxes_triggered.indexOf(be.box_id) > -1) {
        triggeredBoxEvents.push(be);
      } else {
        otherBoxEvents.push(be);
      }
    });
    return { triggeredBoxEvents, otherBoxEvents };
  }

  ensureBoxEventLocationSlug(boxEvent) {
    // Due to the bug on Makai where certain BoxEvents are not properly storing location strings, we will temporarily
    // just set the BoxEvent.location field to the current location of the box.
    const fixedLocationSlug = typeof boxEvent.location !== 'string'
        ? this.getCurrentOpqBoxLocationSlug(boxEvent)
        : null;
    if (fixedLocationSlug) {
      const be = { ...boxEvent };
      be.location = fixedLocationSlug;
      return be;
    }
    return boxEvent;
  }

  getCurrentOpqBoxLocationSlug(boxEvent) {
    const { opqBoxes } = this.props;
    const opqBox = opqBoxes.find(box => box.box_id === boxEvent.box_id);
    return opqBox ? opqBox.location : null;
  }

  /**
   * Ref methods
   * Read more here: https://reactjs.org/docs/refs-and-the-dom.html
   */

  setLeafletMarkerManagerRef = elem => {
    // Need to store the OpqBoxLeafletMarkerManager child component's ref instance so that we can call its
    // zoomToMarker() method from this component.
    if (elem) {
      this.leafletMarkerManagerElem = elem;
    }
  };

  getLeafletMarkerManagerRef = () => this.leafletMarkerManagerElem;

  setMapDivRef = elem => {
    if (elem) this.mapDivElem = elem;
  };

  getMapDivRef = () => this.mapDivElem;
}

EventViewer.propTypes = {
  ready: PropTypes.bool.isRequired,
  event_id: PropTypes.number.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
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
  };
})(EventViewer);
