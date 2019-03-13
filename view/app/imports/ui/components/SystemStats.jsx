import React from 'react';
import { Loader, Statistic, Header, Segment, Grid, List} from 'semantic-ui-react';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';

/**
 * Display numbers as strings with three significant digits. Use 'K' and 'M' for thousands and millions.
 * @param num
 * @returns A string with the number formatted.
 */
function formatted(num = 0) {
  // Numbers less than 1,000 are just what they are.
  if (num < 1000) {
    return `${num}`;
  }
  // Numbers between 1,000 and 1,000,000 are formatted with 3 digit precision and a 'K'.
  if (num < 1000000) {
    return `${(num / 1000).toPrecision(3)}K`;
  }
  // Numbers more than 1M are formatted with an M.
  return `${(num / 1000000).toPrecision(3)}M`;
}

/** Display system statistics. */
class SystemStatistics extends React.Component {

  helpText = `
  <p>System Stats shows a summary of interesting statistics about this OPQ instance.</p>
  
  <p>Trends: Produced once per minute, trends indicate the high, low, and average values for 
  frequency, voltage, and THD observed by a single box over a given minute.</p>
  
  <p>Events: Produced whenever a box measures frequency, voltage, or THD in excess of a default threshold
  (currently +/- 5% of nominal value.</p>
  
  <p>Measurements: Produced six times a second, these provide instantaneous values for frequency, voltage, and THD. 
  However, only the last 24 hours of Measurement data points are stored in the database. </p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Here's the system stats page. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const stat = this.props.stats[0];
    const headerStyle = { textAlign: 'center' };
    const footerStyle = { textAlign: 'center', paddingTop: '10px' };
    const toDates = [
      { label: 'phenomena', value: formatted(stat.phenomena_count) },
      { label: 'incidents', value: formatted(stat.incidents_count) },
      { label: 'events', value: formatted(stat.events_count) },
      { label: 'trends', value: formatted(stat.trends_count) },
      { label: 'measurements', value: formatted(stat.measurements_count) },
    ];
    const todays = [
      { label: 'phenomena', value: formatted(stat.phenomena_count_today) },
      { label: 'incidents', value: formatted(stat.incidents_count_today) },
      { label: 'events', value: formatted(stat.events_count_today) },
      { label: 'trends', value: formatted(stat.trends_count_today) },
      { label: 'measurements', value: formatted(stat.measurements_count_today) },
    ];
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    const divStyle2 = { paddingLeft: '10px', paddingRight: '10px', marginTop: '5px' };
    const statStyle = { paddingBottom: '10px'};
    return (
      <WidgetPanel title="System Stats" helpText={this.helpText}>
        <Grid container columns="two">
          <Grid.Column textAlign="center">
            <Grid.Row centered><Header as='h3' style={statStyle}>Today</Header></Grid.Row>
            <Grid.Row centered><Statistic value={todays[0].value} label={todays[0].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={todays[1].value} label={todays[1].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={todays[2].value} label={todays[2].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={todays[3].value} label={todays[3].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={todays[4].value} label={todays[4].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
          </Grid.Column>
          <Grid.Column textAlign="center">
            <Grid.Row centered><Header as='h3' style={statStyle}>To Date</Header></Grid.Row>
            <Grid.Row centered><Statistic value={toDates[0].value} label={toDates[0].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={toDates[1].value} label={toDates[1].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={toDates[2].value} label={toDates[2].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={toDates[3].value} label={toDates[3].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
            <Grid.Row centered><Statistic value={toDates[4].value} label={toDates[4].label} size="mini" color="blue" style={statStyle}/></Grid.Row>
          </Grid.Column>
        </Grid>
        <p style={footerStyle}>Last update: {Moment(stat.timestamp).format('MMMM Do YYYY, h:mm:ss a')}</p>
      </WidgetPanel>
    );
  }
}

/** Require an array of Stuff documents in the props. */
SystemStatistics.propTypes = {
  stats: PropTypes.array.isRequired,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const subscription = Meteor.subscribe(SystemStats.getPublicationName());
  return {
    stats: SystemStats.find({}).fetch(),
    ready: subscription.ready(),
  };
})(SystemStatistics);
