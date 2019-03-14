import React from 'react';
import { Loader, Header, Grid } from 'semantic-ui-react';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';

/**
 * Display numbers as strings with three significant digits. Use 'K' and 'M' for thousands and millions.
 * @param num (defaults to 0)
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

  /**
   * Render the Title area.
   * @returns {*}
   */
  renderColumnTitles() {
    return (
      <Grid container columns="two">
        <Grid.Column textAlign="center">
          <Header as='h3'>Today</Header>
        </Grid.Column>
        <Grid.Column textAlign="center">
          <Header as='h3'>To Date</Header>
        </Grid.Column>
      </Grid>
    );
  }

  /**
   * Render each of the entity types.
   * @param name  Incident, Phenomena, etc.
   * @param today The number of entities today.
   * @param toDate The total number of entities
   * @param ttl The time-to-live value.
   * @returns {*}
   */
  renderEntity(name, today, toDate, ttl) {
    return (
      <Grid container>
        <Grid.Row centered columns="two" style={{ padding: 0 }}>
          <Grid.Column textAlign="center">
            <Header as='h3' color="blue">{formatted(today)}</Header>
          </Grid.Column>
          <Grid.Column textAlign="center">
            <Header as='h3' color="blue">{formatted(toDate)}</Header>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row centered columns="one" style={{ padding: 0 }}>
          <Grid.Column textAlign="center">
            <b>{name}</b>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row centered columns="one" style={{ padding: 0 }}>
          <Grid.Column textAlign="center">
            TTL: {ttl}
          </Grid.Column>
        </Grid.Row>
        <Grid.Row columns="one" style={{ padding: 0 }}>
          <Grid.Column>
            <hr />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    );
  }

  /** Here's the system stats page. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const stat = this.props.stats[0] || {};
    const footerStyle = { textAlign: 'center', paddingTop: '10px' };
    return (
      <WidgetPanel title="System Stats" helpText={this.helpText}>
        {this.renderColumnTitles()}
        {this.renderEntity('PHENOMENA', stat.phenomena_count_today, stat.phenomena_count, '?')}
        {this.renderEntity('INCIDENTS', stat.incidents_count_today, stat.incidents_count, '?')}
        {this.renderEntity('EVENTS', stat.events_count_today, stat.events_count, '?')}
        {this.renderEntity('TRENDS', stat.trends_count_today, stat.trends_count, '?')}
        {this.renderEntity('MEASUREMENTS', stat.measurements_count_today, stat.measurements_count, '?')}
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
