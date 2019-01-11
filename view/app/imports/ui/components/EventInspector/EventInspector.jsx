import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { withRouter, Link } from 'react-router-dom';
import { Grid, Input, Button, Loader, Table } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Lodash from 'lodash';
import QueryString from 'query-string';

import WidgetPanel from '../../layouts/WidgetPanel';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { getEventsInRange } from '../../../api/events/EventsCollection.methods';
import BoxSelector from '../../layouts/BoxSelector';

/** Allows for the searching of past events, displaying results in a sortable table. */
class EventInspector extends React.Component {
  constructor(props) {
    super(props);

    const end = Moment();
    const start = Moment(end).subtract(1, 'day');

    this.state = {
      start: start.format('YYYY-MM-DDTHH:mm:ss'),
      end: end.format('YYYY-MM-DDTHH:mm:ss'),
      loading: false,
      loaded: false,
      selectedBoxes: [],
      events: [],
      column: null,
      direction: null, // Either 'ascending', 'descending', or null
    };
  }

  componentDidMount() {
    const { start, end } = this.state;
    const urlQueryObj = this.getUrlQueryObj();
    if (urlQueryObj) {
      // If startTime and endTime url params are not specified, will by default use the values set in constructor.
      // This also makes it much simpler to internally link to the event inspector, as we only need to specify the
      // boxes parameter in the url; the startTime and endTime params will automatically be created w/ default values.
      this.setState({
        selectedBoxes: urlQueryObj.boxes.split(','),
        start: urlQueryObj.startTime || start,
        end: urlQueryObj.endTime || end,
      }, () => this.getEvents());
    }
  }

  helpText = `
  <p>The Event Inspector lets you search for past events within specified parameters:</p>
  
  <p>Start and End: Select a starting and ending date/time to search between.</p>
  
  <p>Boxes: select one or more boxes whose events you are interested in.</p>
  
  <p>For each event listed, you can view more information about the event, including event waveforms, by clicking the
  "Details" button</p>
  `;

  /**
   * Render Methods
   */

  render() {
    return this.props.ready ? this.renderPage() : <Loader active content='Loading...'/>;
  }

  renderPage() {
    return (
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
    );
  }

  renderSortableTable() {
    const { events, column, direction } = this.state;

    return (
        <Table sortable celled fixed striped>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell
                  sorted={column === 'event_id' ? direction : null}
                  onClick={this.handleTableSort('event_id')}
              >
                Event ID
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'type' ? direction : null}
                  onClick={this.handleTableSort('type')}
              >
                Type
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'boxes_triggered' ? direction : null}
                  onClick={this.handleTableSort('boxes_triggered')}
              >
                Boxes Triggered
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'target_event_start_timestamp_ms' ? direction : null}
                  onClick={this.handleTableSort('target_event_start_timestamp_ms')}
              >
                Start Time
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'target_event_end_timestamp_ms' ? direction : null}
                  onClick={this.handleTableSort('target_event_end_timestamp_ms')}
              >
                End Time
              </Table.HeaderCell>
              <Table.HeaderCell
                  sorted={column === 'duration' ? direction : null}
                  onClick={this.handleTableSort('duration')}
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
                    <Button disabled={boxes_received.length === 0}
                            color='blue'
                            as={Link}
                            to={{ pathname: `/inspector/event/${event_id}` }}>
                      Details
                    </Button>
                  </Table.Cell>
                </Table.Row>
            ))}
          </Table.Body>
        </Table>
    );
  }

  /**
   * Event Handlers
   */

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
            this.setState({
              events: eventsWithDuration,
              loading: false,
              loaded: true,
            }, () => this.handleTableSort('_resetToDefaultState')());
          },
      );
    });
  };

  /* Adapted from example shown here: https://react.semantic-ui.com/collections/table/#variations-sortable */
  handleTableSort = clickedColumn => () => {
    const { column, direction } = this.state;
    const DEFAULT_SORT_COLUMN = 'event_id';

    // Sort event data and update state, triggering re-render of table.
    if (clickedColumn === '_resetToDefaultState') {
      // Reset to default sorting state. Currently, this is triggered each time we (re)submit the form.
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
  };

  /**
   * Helper/Misc Methods
   */

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
}

EventInspector.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array,
  location: PropTypes.object.isRequired, // From withRouter
  history: PropTypes.object.isRequired, // From withRouter
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
  withRouter,
])(EventInspector);
