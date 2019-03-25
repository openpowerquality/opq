import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { withRouter, Link } from 'react-router-dom';
import { Grid, Input, Button, Loader, Table, Dropdown } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Lodash from 'lodash';
import QueryString from 'query-string';

import WidgetPanel from '../../layouts/WidgetPanel';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';
import { Incidents } from '../../../api/incidents/IncidentsCollection';
import { getIncidentsInRange } from '../../../api/incidents/IncidentsCollection.methods';

/** Allows for the searching of past Incidents, displaying results in a sortable table. */
class IncidentInspector extends React.Component {
    constructor(props) {
        super(props);

        const end = Moment();
        const start = Moment(end).subtract(1, 'day');

        this.state = {
            start: start.format('YYYY-MM-DDTHH:mm:ss'),
            end: end.format('YYYY-MM-DDTHH:mm:ss'),
            loading: false,
            loaded: false,
            selectedBoxes: ['ALL'],
            selectedClassifications: ['ALL'],
            selectedIeeeDurations: ['ALL'],
            incidents: [],
            column: null,
            direction: null, // Either 'ascending', 'descending', or null
        };
    }

    componentDidMount() {
        const { start, end } = this.state;
        const urlQueryObj = this.getUrlQueryObj();
        if (urlQueryObj) {
            // If startTime and endTime url params are not specified, will by default use the values set in constructor.
            // This also makes it much simpler to internally link to the inspector, as we only need to specify the
            // boxes parameter in the url; the startTime and endTime params will be created w/ default values.
            this.setState({
                selectedBoxes: urlQueryObj.boxes,
                start: urlQueryObj.startTime || start,
                end: urlQueryObj.endTime || end,
                selectedClassifications: urlQueryObj.classifications,
                selectedIeeeDurations: urlQueryObj.ieeeDurations,
            }, () => this.getIncidents());
        }
    }

    helpText = `
  <p>The Incident Inspector lets you search for past incidents within specified parameters:</p>
  
  <p>Start and End: Select a starting and ending date/time to search between.</p>
  
  <p>Boxes: select one or more boxes whose incidents you are interested in.</p>
  
  <p>You can view information about the incident, including incident waveforms, by clicking the "Details" button</p>
  `;

  /**
   * Render Methods
   */

  render() {
      return this.props.ready ? this.renderPage() : <Loader active content='Loading...'/>;
  }

  renderPage() {
    // Create dropdown options, also adding an additional 'ALL' option for each dropdown.
    const boxIdDropdownOptions = this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }));
    boxIdDropdownOptions.unshift({ text: 'All Boxes', value: 'ALL' });
    const classificationsDropdownOptions = Incidents.classificationTypes.map(type => ({ text: type, value: type }));
    classificationsDropdownOptions.unshift({ text: 'All Classifications', value: 'ALL' });
    const ieeeDurationsDropdownOptions = Incidents.ieeeDurationTypes.map(type => ({ text: type, value: type }));
    ieeeDurationsDropdownOptions.unshift({ text: 'All Durations', value: 'ALL' });

    return (
        <WidgetPanel title='Incident Inspector' helpText={this.helpText}>
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
                <Dropdown multiple search selection fluid
                          placeholder='Boxes'
                          options={boxIdDropdownOptions}
                          onChange={this.onChangeBoxes}
                          value={this.state.selectedBoxes}/>
              </Grid.Column>
              <Grid.Column width={3}>
                <Button content='Submit' fluid onClick={this.getIncidents}/>
              </Grid.Column>
            </Grid.Row>
            <Grid.Row>
              <Grid.Column width={4}>
                <Dropdown multiple search selection fluid
                          placeholder='Classification'
                          options={classificationsDropdownOptions}
                          onChange={this.onChangeClassifications}
                          value={this.state.selectedClassifications}/>
              </Grid.Column>
              <Grid.Column width={4}>
                <Dropdown multiple search selection fluid
                          placeholder='IEEE Duration'
                          options={ieeeDurationsDropdownOptions}
                          onChange={this.onChangeIeeeDurations}
                          value={this.state.selectedIeeeDurations}/>
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
        const { incidents, column, direction } = this.state;

        return (
            <Table sortable celled fixed striped>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell
                            sorted={column === 'incident_id' ? direction : null}
                            onClick={this.handleTableSort('incident_id')}
                        >
                            Incident ID
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'box_id' ? direction : null}
                            onClick={this.handleTableSort('box_id')}
                        >
                          Box ID
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'classifications' ? direction : null}
                            onClick={this.handleTableSort('classifications')}
                        >
                            Classifications
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'ieee_duration' ? direction : null}
                            onClick={this.handleTableSort('ieee_duration')}
                        >
                          IEEE Duration
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'start_timestamp_ms' ? direction : null}
                            onClick={this.handleTableSort('start_timestamp_ms')}
                        >
                            Start Time
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
                    {incidents.map(({ incident_id, classifications, ieee_duration, box_id, start_timestamp_ms, duration }) => (
                        <Table.Row key={incident_id}>
                            <Table.Cell>{incident_id}</Table.Cell>
                            <Table.Cell>{box_id}</Table.Cell>
                            <Table.Cell>{classifications}</Table.Cell>
                            <Table.Cell>{ieee_duration}</Table.Cell>
                            <Table.Cell>{Moment(start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</Table.Cell>
                            <Table.Cell>{typeof duration === 'number' ? duration.toFixed(2) : duration}</Table.Cell>
                            <Table.Cell>
                                <Button color='blue'
                                        as={Link}
                                        to={{ pathname: `/inspector/incident/${incident_id}` }}>
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
    onChangeBoxes = (event, data) => { this.setState({ selectedBoxes: data.value.sort() }); };
    onChangeClassifications = (event, data) => { this.setState({ selectedClassifications: data.value }); };
    onChangeIeeeDurations = (event, data) => { this.setState({ selectedIeeeDurations: data.value }); };

    getIncidents = () => {
        const { start, end, selectedBoxes, selectedClassifications, selectedIeeeDurations } = this.state;
        const startTime_ms = Moment(start).valueOf();
        const endTime_ms = Moment(end).valueOf();
        this.setUrlQuery({
          boxIds: selectedBoxes,
          startTime: startTime_ms,
          endTime: endTime_ms,
          classifications: selectedClassifications,
          ieeeDurations: selectedIeeeDurations,
        });
        this.setState({ loading: true }, () => {
            getIncidentsInRange.call(
                {
                    boxIds: selectedBoxes,
                    startTime_ms,
                    endTime_ms,
                    classifications: selectedClassifications,
                    ieee_durations: selectedIeeeDurations,
                },
                (error, incidents) => {
                    if (error) {
                      console.log(error);
                      this.setState({ loading: false, loaded: true });
                    } else {
                      // Calculate and add a 'duration' property for each incident. This is because we want to be able
                      // to sort on the duration field (otherwise we could've just calculated duration in the render method).
                      const incidentsWithDuration = incidents.map(incident => {
                        // eslint-disable-next-line no-param-reassign
                        incident.duration = incident.end_timestamp_ms - incident.start_timestamp_ms;
                        return incident;
                      });
                      this.setState({
                        incidents: incidentsWithDuration,
                        loading: false,
                        loaded: true,
                      }, () => this.handleTableSort('_resetToDefaultState')());
                    }
                },
            );
        });
    };

    /* Adapted from example shown here: https://react.semantic-ui.com/collections/table/#variations-sortable */
    handleTableSort = clickedColumn => () => {
        const { column, direction } = this.state;
        const DEFAULT_SORT_COLUMN = 'incident_id';

        // Sort incidents and update state, triggering re-render of table.
        if (clickedColumn === '_resetToDefaultState') {
            // Reset to default sorting state. Currently, this is triggered each time we (re)submit the form.
            this.setState(state => ({
                column: DEFAULT_SORT_COLUMN,
                direction: 'descending',
                incidents: Lodash.sortBy(state.incidents, [DEFAULT_SORT_COLUMN]).reverse(), // SortBy is asc by default.
            }));
        } else if (column !== clickedColumn) {
            // If a different column is clicked, we sort it (desc).
            this.setState(state => ({
                column: clickedColumn,
                direction: 'descending',
                incidents: Lodash.sortBy(state.incidents, [clickedColumn]).reverse(), // SortBy is asc by default.
            }));
        } else {
            // If the same column is clicked, we can simply reverse its ordering.
            this.setState(state => ({
                incidents: state.incidents.reverse(),
                direction: direction === 'descending' ? 'ascending' : 'descending',
            }));
        }
    };

    /**
     * Helper/Misc Methods
     */

    setUrlQuery({ boxIds, startTime, endTime, classifications, ieeeDurations }) {
        const startTimeFormatted = Moment(startTime).format('YYYY-MM-DDTHH:mm:ss');
        const endTimeFormatted = Moment(endTime).format('YYYY-MM-DDTHH:mm:ss');
        const queryStringObj = {
          startTime: startTimeFormatted,
          endTime: endTimeFormatted,
          boxes: boxIds,
          classifications: classifications,
          ieeeDurations: ieeeDurations,
        };
        const queryStr = QueryString.stringify(queryStringObj, { sort: false, encode: false, arrayFormat: 'comma' });
        // HashRouter doesn't seem to play nicely with history.push(), so we use replace() instead. The only loss is
        // that we can no longer use back/forward on the browser history to navigate between previous inspector queries.
        this.props.history.replace({
            pathname: this.props.location.pathname,
            search: queryStr,
        });
    }

    getUrlQueryObj() {
      const currQueryString = this.props.location.search;
      if (!currQueryString) return null;
      const qs = QueryString.parse(currQueryString, { arrayFormat: 'comma' });
      // QS properly interprets query keys such as 'boxes=1000,1001' as an array, but incorrectly interprets
      // 'boxes=1000' as just a string. This makes sense, because QS has no real way of knowing that this key should
      // be treated as an array. To fix, we just manually create an array if these keys only have 1 element.
      if (qs.boxes && !Array.isArray(qs.boxes)) qs.boxes = qs.boxes.split(',');
      if (qs.classifications && !Array.isArray(qs.classifications)) qs.classifications = qs.classifications.split(',');
      if (qs.ieeeDurations && !Array.isArray(qs.ieeeDurations)) qs.ieeeDurations = qs.ieeeDurations.split(',');
      return qs;
    }
}

IncidentInspector.propTypes = {
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
])(IncidentInspector);
