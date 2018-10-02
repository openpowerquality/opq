import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Link } from 'react-router-dom';
import { Grid, Input, Button, Loader, Table } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Lodash from 'lodash';
import QueryString from 'query-string';

import WidgetPanel from '../../layouts/WidgetPanel';
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
      column: null,
      direction: null, // Either 'ascending', 'descending', or null
    };

    this.handleSort.bind(this);
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
    // Previously, we were able to specify an initial box ID to display events for by utilizing React-Router's location
    // state object. However, we can consider removing this now that we are specifying box IDs in the url query.
    // if (initialBoxIds && initialBoxIds.length) {
    //   this.setState({ selectedBoxes: initialBoxIds }, () => this.getEvents());
    // }
    console.log(this.getUrlQueryObj());
    const urlQueryObj = this.getUrlQueryObj();
    if (urlQueryObj) {
      this.setState({
        selectedBoxes: urlQueryObj.boxes.split(','),
        start: urlQueryObj.startTime,
        end: urlQueryObj.endTime,
      }, () => this.getEvents());
    }
  }


  setUrlQuery(boxIds, startTime_ms, endTime_ms) {
    const startTimeFormatted = Moment(startTime_ms).format('YYYY-MM-DDTHH:mm:ss');
    const endTimeFormatted = Moment(endTime_ms).format('YYYY-MM-DDTHH:mm:ss');
    // HashRouter doesn't seem to play nicely with history.push(), so we use replace() instead. The only loss is
    // that we can no longer use back/forward on the browser history to navigate between previous inspector queries.
    this.props.history.replace({
      pathname: this.props.location.pathname,
      search: `?startTime=${startTimeFormatted}&endTime=${endTimeFormatted}&boxes=${boxIds}`,
    });
  }

  getUrlQueryObj() {
    const currQueryString = this.props.location.search;
    return currQueryString ? QueryString.parse(currQueryString) : null;
  }

  handleSort(clickedColumn) {
    const { column, direction } = this.state;
    const DEFAULT_SORT_COLUMN = 'event_id';

    // Sort event data and update state, triggering re-render of table.
    if (!clickedColumn) {
      // If no column is specified, we sort by the default column specified above. Currently, this is triggered each
      // time we (re)submit the form.
      this.setState(state => ({
        column: DEFAULT_SORT_COLUMN,
        direction: 'descending',
        events: Lodash.sortBy(state.events, [DEFAULT_SORT_COLUMN]).reverse(), // SortBy is asc by default.
      }));
    } else if (column !== clickedColumn) {
      // If a different column is clicked, we sort it (desc).
      this.setState(state => ({
        column: clickedColumn,
        direction: 'descending',
        events: Lodash.sortBy(state.events, [clickedColumn]).reverse(), // SortBy is asc by default.
      }));
    } else {
      // If the same column is clicked, we can simply reverse its ordering.
      this.setState(state => ({
        events: state.events.reverse(),
        direction: direction === 'descending' ? 'ascending' : 'descending',
      }));
    }
  }

  renderSortableTable() {
    const { events, column, direction } = this.state;

    return (
        <Table sortable celled fixed striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell
                  sorted={column === 'event_id' ? direction : null}
                  onClick={this.handleSort.bind(this, 'event_id')}
              >
                Event ID
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'type' ? direction : null}
                  onClick={this.handleSort.bind(this, 'type')}
              >
                Type
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'boxes_triggered' ? direction : null}
                  onClick={this.handleSort.bind(this, 'boxes_triggered')}
              >
                Boxes Triggered
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'target_event_start_timestamp_ms' ? direction : null}
                  onClick={this.handleSort.bind(this, 'target_event_start_timestamp_ms')}
              >
                Start Time
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'target_event_end_timestamp_ms' ? direction : null}
                  onClick={this.handleSort.bind(this, 'target_event_end_timestamp_ms')}
              >
                End Time
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'duration' ? direction : null}
                  onClick={this.handleSort.bind(this, 'duration')}
              >
                Duration (ms)
              </Table.HeaderCell>
              <Table.HeaderCell>Details</Table.HeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {events.map(({ event_id, type, boxes_triggered, boxes_received, target_event_start_timestamp_ms,
                           target_event_end_timestamp_ms }) => (
              <Table.Row key={event_id}>
              <Table.Cell>{event_id}</Table.Cell>
              <Table.Cell>{type}</Table.Cell>
              <Table.Cell>{boxes_triggered}</Table.Cell>
              <Table.Cell>{Moment(target_event_start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</Table.Cell>
              <Table.Cell>{Moment(target_event_end_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</Table.Cell>
              <Table.Cell>{target_event_end_timestamp_ms - target_event_start_timestamp_ms}</Table.Cell>
              <Table.Cell>
                <Button
                    disabled={boxes_received.length === 0}
                    color='blue'
                    as={Link}
                    to={{
                      pathname: `/inspector/event/${event_id}`,
                    }}>
                  Details ({boxes_received.length})
                </Button>
              </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
    );
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
                    {this.renderSortableTable()}
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
    const startTime_ms = Moment(start).valueOf();
    const endTime_ms = Moment(end).valueOf();
    this.setUrlQuery(selectedBoxes, startTime_ms, endTime_ms);
    this.setState({ loading: true }, () => {
      getEventsInRange.call(
        {
          boxIDs: selectedBoxes,
          startTime_ms,
          endTime_ms,
        },
        (error, events) => {
          // Calculate and add a 'duration' property for each event. This is necessary because we want to be able to
          // sort on the duration field (otherwise we could've just calculated duration in the render method).
          const eventsWithDuration = events.map(event => {
            // eslint-disable-next-line no-param-reassign
            event.duration = event.target_event_end_timestamp_ms - event.target_event_start_timestamp_ms;
            return event;
          });
          this.setState({ events: eventsWithDuration, loading: false, loaded: true }, () => this.handleSort());
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
