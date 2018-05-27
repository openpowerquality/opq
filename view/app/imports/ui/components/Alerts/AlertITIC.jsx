import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Input, Button, Dropdown, Loader, Segment, Icon } from 'semantic-ui-react';
import Moment from 'moment/moment';

import WidgetPanel from '../../layouts/WidgetPanel';
import EventSummary from '../EventInspector/EventSummary';
import { Locations } from '../../../api/locations/LocationsCollection';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { getBoxesInLoc } from '../../../api/opq-boxes/OpqBoxesCollectionMethods';
import { getBoxEventsByType } from '../../../api/box-events/BoxEventsCollectionMethods';

/** Displays event details, including the waveform at the time of the event. */
class AlertITIC extends React.Component {
  constructor(props) {
    super(props);

    const end = Moment();
    const start = Moment(end).subtract(1, 'day');

    this.state = {
      start: start.format('YYYY-MM-DDTHH:mm'),
      end: end.format('YYYY-MM-DDTHH:mm'),
      itic_region: '',
      locations: [],
      loading: false,
      loaded: false,
    };
  }

  // eslint-disable-next-line max-len
  helpText = ` <p>Alert ITIC allows you to find specific events you are interested in based on ITIC region, location(s), and a start and end date.</p>
  `;

  render() {

    return this.props.ready ? (
        <WidgetPanel title='ITIC Alert' helpText={this.helpText}>
          <Grid container><Grid.Column width={16}><Grid stackable>
            <Grid.Row>
              <Grid.Column width={8}>
                <Button.Group fluid toggle>
                  <Button active={this.state.itic_region.includes('NO_DAMAGE')}
                          content='No Damage Region'
                          value='NO_DAMAGE'
                          onClick={this.changeITIC}
                          name='itic'/>
                  <Button active={this.state.itic_region.includes('PROHIBITED')}
                          content='Prohibited Region'
                          value='PROHIBITED'
                          onClick={this.changeITIC}
                          name='itic'/>
                </Button.Group>
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column width={4}>
                <Input fluid label='Start' type='datetime-local'
                       defaultValue={this.state.start} onChange={this.changeStart}/>
              </Grid.Column>
              <Grid.Column width={4}>
                <Input fluid label='End' type='datetime-local'
                       defaultValue={this.state.end} onChange={this.changeEnd}/>
              </Grid.Column>
              <Grid.Column width={5}>
                <Dropdown multiple search selection fluid
                          placeholder='Locations'
                          options={this.props.locations.map(location => ({ text: `${location}`, value: location }))}
                          onChange={this.changeSelectedLocations}
                          value={this.state.locations}/>
              </Grid.Column>
              <Grid.Column width={3}>
                <Button content='Submit' fluid onClick={this.getEvents}/>
              </Grid.Column>
            </Grid.Row>
            {this.state.loading ? (
                <Grid.Row>
                  <Grid.Column>
                    <Loader active content=' '/>
                  </Grid.Column>
                </Grid.Row>
            ) : ''}
            {this.state.loaded ? (

                <Grid.Row>
                  <Grid.Column width={16}>
                    <Segment compact color='yellow' secondary raised size='huge'>
                      <Icon name='alarm'/>
                      There have been <b>{this.state.events.length}</b> occurrences
                    </Segment>
                    {this.state.events.map(event => (
                        <EventSummary event={event} key={event.event_id}/>
                    ))}
                  </Grid.Column>
                </Grid.Row>
            ) : ''}
          </Grid></Grid.Column></Grid>
        </WidgetPanel>
    ) : '';
  }

  changeStart = (event, data) => {
    this.setState({ start: data.value });
  };
  changeEnd = (event, data) => {
    this.setState({ end: data.value });
  };
  changeITIC = (event, data) => {
    this.setState({ itic_region: data.value });
  };
  changeSelectedLocations = (event, data) => {
    this.setState({ locations: data.value.sort() });
  };

  getEvents = () => {
    const { itic_region, locations, start, end } = this.state;
    const boxes = getBoxesInLoc.call({ locations });
    this.setState({ loading: true }, () => {
      getBoxEventsByType.call(
          {
            itic_region,
            boxIDs: boxes,
            startTime_ms: Moment(start).valueOf(),
            endTime_ms: Moment(end).valueOf(),
          },
          (error, events) => {
            this.setState({ events, loading: false, loaded: true });
          },
      );
    });
  };
}

AlertITIC.propTypes = {
  ready: PropTypes.bool.isRequired,
  locations: PropTypes.array,
};

export default withTracker(() => {
  const locSub = Meteor.subscribe(Locations.getPublicationName());
  const boxSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    ready: locSub.ready() && boxSub.ready(),
    locations: Locations.getLocations(),
    boxIds: OpqBoxes.findBoxIds(),
  };
})(AlertITIC);
