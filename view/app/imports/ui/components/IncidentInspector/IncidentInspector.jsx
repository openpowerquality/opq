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
import BoxSelector from '../../layouts/BoxSelector';
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
            selectedBoxes: [],
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
            // boxes parameter in the url; the startTime and endTime params will automatically be created w/ default values.
            this.setState({
                selectedBoxes: urlQueryObj.boxes.split(','),
                start: urlQueryObj.startTime || start,
                end: urlQueryObj.endTime || end,
            }, () => this.getIncidents());
        }
    }

    helpText = `
  <p>The Incident Inspector lets you search for past incidents within specified parameters:</p>
  
  <p>Start and End: Select a starting and ending date/time to search between.</p>
  
  <p>Boxes: select one or more boxes whose incidents you are interested in.</p>
  
  <p>You can view more information about the incident, including incident waveforms, by clicking the "Details" button</p>
  `;

    /**
     * Render Methods
     */

    render() {
        return this.props.ready ? this.renderPage() : <Loader active content='Loading...'/>;
    }

    renderPage() {
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
                            <BoxSelector boxIDs={this.props.boxIDs}
                                         onChange={this.changeSelectedBoxes}
                                         value={this.state.selectedBoxes}/>
                        </Grid.Column>
                        <Grid.Column width={3}>
                            <Button content='Submit' fluid onClick={this.getIncidents}/>
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
                            sorted={column === 'classifications' ? direction : null}
                            onClick={this.handleTableSort('classifications')}
                        >
                            Classifications
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'box_id' ? direction : null}
                            onClick={this.handleTableSort('box_id')}
                        >
                            Box ID
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'start_timestamp_ms' ? direction : null}
                            onClick={this.handleTableSort('start_timestamp_ms')}
                        >
                            Start Time
                        </Table.HeaderCell>
                        <Table.HeaderCell
                            sorted={column === 'end_timestamp_ms' ? direction : null}
                            onClick={this.handleTableSort('end_timestamp_ms')}
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
                    {incidents.map(({ incident_id, classifications, box_id, start_timestamp_ms, end_timestamp_ms }) => (
                        <Table.Row key={incident_id}>
                            <Table.Cell>{incident_id}</Table.Cell>
                            <Table.Cell>{classifications}</Table.Cell>
                            <Table.Cell>{box_id}</Table.Cell>
                            <Table.Cell>{Moment(start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</Table.Cell>
                            <Table.Cell>{Moment(end_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</Table.Cell>
                            <Table.Cell>{end_timestamp_ms - start_timestamp_ms}</Table.Cell>
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
    changeSelectedBoxes = (event, data) => { this.setState({ selectedBoxes: data.value.sort() }); };

    getIncidents = () => {
        const { selectedBoxes, start, end } = this.state;
        const startTime_ms = Moment(start).valueOf();
        const endTime_ms = Moment(end).valueOf();
        this.setUrlQuery(selectedBoxes, startTime_ms, endTime_ms);
        this.setState({ loading: true }, () => {
            getIncidentsInRange.call(
                {
                    boxIds: selectedBoxes,
                    startTime_ms,
                    endTime_ms,
                },
                (error, incidents) => {
                    // Calculate and add a 'duration' property for each incident. This is necessary because we want to be able to
                    // sort on the duration field (otherwise we could've just calculated duration in the render method).
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
