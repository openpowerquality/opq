import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Loader, Message, Icon, Segment, Header, List, Tab, Container } from 'semantic-ui-react';
import { Map, TileLayer, ZoomControl } from 'react-leaflet';
import Moment from 'moment/moment';
import LeafletMarkerManager from '../BoxMap/LeafletMarkerManager';
import WidgetPanel from '../../layouts/WidgetPanel';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { Locations } from '../../../api/locations/LocationsCollection';
import { getIncidentByIncidentID } from '../../../api/incidents/IncidentsCollection.methods';
import { getEventWaveformViewerData } from '../../../api/events/EventsCollection.methods';
import WaveformViewer from '../WaveformViewer';

/** Displays details of an individual Incident */
class IncidentViewer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      incident: null,
      eventWaveformViewerData: null,
      errorReason: null,
    };
  }

  componentDidMount() {
    const { incident_id } = this.props;
    this.retrieveInitialData(incident_id);
  }

  helpText = `
  <p>The Incident Viewer component displays the details of an incident, including waveform data collected from the
  triggered OPQBox during the time of the incident.</p>
  `;

  /**
   * Render Methods
   */

  render() {
    if (this.state.errorReason) return this.renderError(this.state.errorReason);
    return (this.props.ready && !this.state.isLoading) ? this.renderPage() : <Loader active content='Loading...'/>;
  }

  renderPage() {
    return (
        <Grid container stackable>
          <Grid.Column width={16}>
            <WidgetPanel title='Incident Viewer' helpText={this.helpText}>
              <Grid container>
                <Grid.Column width={4}>{this.renderSidePanel()}</Grid.Column>
                <Grid.Column width={12}>
                  <Grid>
                    <Grid.Column width={16}>{this.renderHeader()}</Grid.Column>
                    <Grid.Column width={16}>{this.renderIncidentDetailsCards()}</Grid.Column>
                    <Grid.Column width={16}>{this.renderIncidentWaveform()}</Grid.Column>
                    <Grid.Column width={16}>{this.renderEventWaveforms()}</Grid.Column>
                  </Grid>
                </Grid.Column>
              </Grid>
            </WidgetPanel>
          </Grid.Column>
        </Grid>
    );
  }

  renderHeader() {
    const { incident } = this.state;
    const incidentTime = incident ? Moment(incident.start_timestamp_ms).format('HH:mm:ss - D MMMM, Y') : null;
    return incident ? (
        <Header as='h2'>
          <Header.Content>
            Incident Summary (#{incident.incident_id})
            <Header.Subheader>
              <Icon name='clock' style={{ marginRight: '3px' }} />
              {incidentTime}
            </Header.Subheader>
          </Header.Content>
        </Header>
    ) : null;
  }

  renderIncidentDetailsCards() {
    const { incident } = this.state;

    const IncidentDetailsCard = ({ header, subheader, icon, color }) => (
        <Grid.Column>
          <Segment inverted={!!color} color={color} >
            <Header as='h3'>
              {icon ? <Icon name={icon} /> : null }
              <Header.Content>
                {header}
                <Header.Subheader>{subheader}</Header.Subheader>
              </Header.Content>
            </Header>
          </Segment>
        </Grid.Column>
    );

    const incidentDuration = incident ? (incident.end_timestamp_ms - incident.start_timestamp_ms).toFixed(3) : null;
    const devFromNominal = incident && incident.deviation_from_nominal
        ? incident.deviation_from_nominal.toFixed(4)
        : null;

    return incident ? (
        <Grid columns={4}>
          <IncidentDetailsCard header='Classifications' subheader={incident.classifications} icon='lightning' color='yellow' />
          <IncidentDetailsCard header='IEEE Duration' subheader={incident.ieee_duration} icon='clock' color='green' />
          <IncidentDetailsCard header='Dev. from Nominal' subheader={devFromNominal} icon='chart line' color='teal' />
          <IncidentDetailsCard header='Duration' subheader={`${incidentDuration} ms`} icon='clock' color='blue' />
        </Grid>
    ) : null;
  }

  renderIncidentWaveform() {
    const { opqBoxes } = this.props;
    const { incident } = this.state;

    const opqBox = opqBoxes.find(box => box.box_id === incident.box_id);

    return incident && incident.gridfs_filename ? (
        <WaveformViewer gridfs_filename={incident.gridfs_filename}
                        opqBoxDoc={opqBox}
                        startTimeMs={incident.start_timestamp_ms}
                        title={'Incident Waveform'}
                        displayOnLoad/>
    ) : null;
  }

  renderEventWaveforms() {
    const { eventWaveformViewerData, incident } = this.state;

    // Only display the BoxEvent matching Incident.box_id
    let originatingBox = null;
    if (eventWaveformViewerData && incident) {
      const combined = [...eventWaveformViewerData.triggeredBoxes, ...eventWaveformViewerData.otherBoxes];
      originatingBox = combined.find(({ boxEvent }) => boxEvent.box_id === incident.box_id);
    }

    return originatingBox ? (
        <WaveformViewer key={originatingBox.boxEvent.data_fs_filename}
                        gridfs_filename={originatingBox.boxEvent.data_fs_filename}
                        opqBoxDoc={originatingBox.opqBox}
                        startTimeMs={originatingBox.boxEvent.event_start_timestamp_ms}
                        title={`Originating Event Waveform (Event #${originatingBox.boxEvent.event_id}, Box #${originatingBox.boxEvent.box_id})`}
                        displayOnLoad/>
    ) : null;
  }

  renderSidePanel() {
    const panes = [
      { menuItem: 'Incident Details', render: () => <Tab.Pane as={Container}>{this.renderIncidentDetailsList()}</Tab.Pane> },
      { menuItem: 'Metadata', render: () => <Tab.Pane as={Container}>{this.renderMetadataList()}</Tab.Pane> },
      { menuItem: 'Related', render: () => <Tab.Pane as={Container}>List similar stuff here</Tab.Pane> },
    ];

    return (
        <Segment.Group>
          <Segment style={{ padding: '0px' }}>
            {this.renderMap()}
          </Segment>
          <Segment>
            <Tab menu={{ secondary: true, pointing: true }} panes={panes} />
          </Segment>
        </Segment.Group>
    );
  }

  renderMap() {
    const { incident } = this.state;
    const { locations } = this.props;

    const incidentLocation = locations.find(loc => loc.slug === incident.location);
    const mapCenter = this.getLocationCoords(incidentLocation);

    // It seems that the dropdown menu from the navigation bar has a z-index of 11, which results in the menu clipping
    // beneath the Leaflet map. We set the map's z-index to 10 to fix this.
    const mapStyle = { height: '100%', zIndex: 10 };

    return incident ? (
        <div style={{ height: '300px', width: '100%' }}>
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
                locations={[incidentLocation]}
                markerLabelFunc={this.createMarkerLabel} />
          </Map>
        </div>
    ) : null;
  }

  renderIncidentDetailsList() {
    const { incident } = this.state;

    const startTime = incident ? Moment(incident.start_timestamp_ms).format('HH:mm:ss.SSS - YYYY-MM-DD') : null;
    const endTime = incident ? Moment(incident.end_timestamp_ms).format('HH:mm:ss.SSS - YYYY-MM-DD') : null;
    const classifications = incident.classifications && incident.classifications.length ? incident.classifications : 'None';
    const annotations = incident.annotations && incident.annotations.length ? incident.annotations : 'None';

    const ListItem = ({ header, description, icon }) => (
        <List.Item>
          <List.Icon name={icon} size='large' verticalAlign='middle' />
          <List.Content>
            <List.Header as='a'>{header}</List.Header>
            <List.Description>{description}</List.Description>
          </List.Content>
        </List.Item>
    );

    return incident ? (
        <List divided>
          <ListItem header='Incident ID' description={incident.incident_id} icon='hashtag' />
          <ListItem header='Box ID' description={incident.box_id} icon='hashtag' />
          <ListItem header='Event ID' description={incident.event_id} icon='hashtag' />
          <ListItem header='Start Time' description={startTime} icon='hourglass start' />
          <ListItem header='End Time' description={endTime} icon='hourglass end' />
          <ListItem header='Location' description={incident.location} icon='marker' />
          <ListItem header='Measurement Type' description={incident.measurement_type} icon='lightning' />
          <ListItem header='Deviation From Nominal' description={incident.deviation_from_nominal} icon='chart line' />
          <ListItem header='Classifications' description={classifications} icon='lightning' />
          <ListItem header='IEEE Duration' description={incident.ieee_duration} icon='clock' />
          <ListItem header='Annotations' description={annotations} icon='tag' />
        </List>
    ) : null;
  }

  renderMetadataList() {
    const { incident } = this.state;

    const ListItem = ({ header, description }) => (
        <List.Item>
          <List.Content>
            <List.Header as='a'>{header}</List.Header>
            <List.Description>
              {typeof description === 'object' ? JSON.stringify(description) : description}
            </List.Description>
          </List.Content>
        </List.Item>
    );

    return incident && incident.metadata && Object.keys(incident.metadata).length > 0 ? (
        <List divided>
          {Object.keys(incident.metadata).map(key => (
              <ListItem key={key} header={key} description={incident.metadata[key]} />
          ))}
        </List>
    ) : 'No metadata for this Incident';
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

  createMarkerLabel = (locationDoc) => {
    const { opqBoxes } = this.props;
    const opqBox = opqBoxes.find(box => box.location === locationDoc.slug);
    return `
      <div>
        <b>${locationDoc.description}</b>
        <b>Box ID ${opqBox.box_id}</b>
      </div>
    `;
  };

  /**
   * Helper/Misc Methods
   */

  retrieveInitialData(incident_id) {
    // Retrieve the corresponding Incident document for the given incident_id.
    this.setState({ isLoading: true }, () => {
      getIncidentByIncidentID.call({ incident_id }, (error, incident) => {
        if (error) {
          console.log(error);
          if (error.error === 'invalid-incident-id') {
            this.setState({ isLoading: false, errorReason: error.reason });
          }
        } else {
          // Retrieve filesnames for the given event_id (so we can display originating Event waveform).
          // eslint-disable-next-line no-lonely-if
          if (incident.event_id > -1) { // OUTAGE Incidents receive an event_id = -1
            getEventWaveformViewerData.call({ event_id: incident.event_id }, (err, eventWaveformViewerData) => {
              if (err) {
                console.log(err);
                if (err.error === 'invalid-event-id') {
                  this.setState({ isLoading: false, errorReason: error.reason });
                }
              } else {
                this.setState({ incident, eventWaveformViewerData, isLoading: false });
              }
            });
          } else {
            this.setState({ incident, isLoading: false });
          }
        }
      });
    });
  }

  getLocationCoords(location) {
    return location ? location.coordinates.slice().reverse() : null;
  }
}

IncidentViewer.propTypes = {
  ready: PropTypes.bool.isRequired,
  incident_id: PropTypes.number.isRequired,
  opqBoxes: PropTypes.array.isRequired,
  locations: PropTypes.array.isRequired,
};

export default withTracker((props) => {
  const locationsSub = Meteor.subscribe(Locations.getCollectionName());
  const opqBoxesSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  const opqBoxes = OpqBoxes.find().fetch();

  return {
    ready: opqBoxesSub.ready() && locationsSub.ready(),
    incident_id: Number(props.match.params.incident_id),
    opqBoxes,
    locations: Locations.find().fetch(),
  };
})(IncidentViewer);
