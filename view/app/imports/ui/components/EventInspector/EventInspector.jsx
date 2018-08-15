import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Input, Button, Dropdown, Loader } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Lodash from 'lodash';

import WidgetPanel from '../../layouts/WidgetPanel';
import EventSummary from './EventSummary';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { getEventsInRange } from '../../../api/events/EventsCollection.methods';
import { withRouterLocationStateAsProps } from '../BoxMap/hocs';
import BoxSelector from '../../layouts/BoxSelector';

/** Displays event details, including the waveform at the time of the event. */
class EventInspector extends React.Component {
  constructor(props) {
    super(props);

    const end = Moment();
    const start = Moment(end).subtract(1, 'day');

    this.state = {
      start: start.format('YYYY-MM-DDTHH:mm'),
      end: end.format('YYYY-MM-DDTHH:mm'),
      loading: false,
      loaded: false,
      selectedBoxes: [],
      events: [],
    };
  }

  helpText = `
  <p>Event Inspector lets you search for an event and look at the details of it, such as the waveform at the time of 
  the event.</p>
  
  <p>Start and End: Select a starting and ending date/time to search between.</p>
  
  <p>Boxes: select one or more boxes whose events you are interested in.</p>
  
  <p>For each event listed, the labeled buttons can be clicked to generate a graph with the waveform at the time of the
  event, for that box.</p>
  `;

  componentDidMount() {
    const { initialBoxIds } = this.props;
    if (initialBoxIds && initialBoxIds.length) {
      this.setState({ selectedBoxes: initialBoxIds }, () => this.getEvents());
    }
  }

  render() {
    return this.props.ready ? (
      <WidgetPanel title='Event Inspector' helpText={this.helpText}>
        <Grid container><Grid.Column width={16}><Grid stackable>
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
              <BoxSelector boxIDs={this.props.boxIDs}
                           onChange={this.changeSelectedBoxes}
                           value={this.state.selectedBoxes}/>
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

  changeStart = (event, data) => { this.setState({ start: data.value }); };
  changeEnd = (event, data) => { this.setState({ end: data.value }); };
  changeSelectedBoxes = (event, data) => { this.setState({ selectedBoxes: data.value.sort() }); };

  getEvents = () => {
    const { selectedBoxes, start, end } = this.state;
    this.setState({ loading: true }, () => {
      getEventsInRange.call(
        {
          boxIDs: selectedBoxes,
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

EventInspector.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array,
  initialBoxIds: PropTypes.array,
};

const withTrackerCallback = () => {
  const sub = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    ready: sub.ready(),
    boxIDs: OpqBoxes.find().fetch().map(box => box.box_id).sort(),
  };
};

// Component/HOC composition
export default Lodash.flowRight([
  withTracker(withTrackerCallback),
  withRouterLocationStateAsProps(['initialBoxIds']),
])(EventInspector);
