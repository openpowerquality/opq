import React from 'react';
import { Loader, Statistic, Header, Segment } from 'semantic-ui-react';
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
function formatted(num) {
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
  
  <p>Measurements: Produced six times a second, these provide instantaneous values for frequency, voltage, and THD.</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** Here's the system stats page. */
  renderPage() { // eslint-disable-line class-methods-use-this

    const missingStats = {
      events_count: 0, box_events_count: 0, measurements_count: 0, opq_boxes_count: 0,
      trends_count: 0, users_count: 0,
    };
    const stat = this.props.stats[0] || missingStats;
    const headerStyle = { textAlign: 'center' };
    const footerStyle = { textAlign: 'center', paddingTop: '10px' };
    const toDateItems = [
      { key: '1', label: 'Trends', value: formatted(stat.trends_count) },
      { key: '2', label: 'Events', value: formatted(stat.events_count) },
      { key: '3', label: 'Measurements', value: formatted(stat.measurements_count) },
    ];
    const todayItems = [
      { key: '1', label: 'Trends', value: stat.trends_count_today },
      { key: '2', label: 'Events', value: stat.events_count_today },
      { key: '3', label: 'Measurements', value: stat.measurements_count_today },
    ];
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    const divStyle2 = { paddingLeft: '10px', paddingRight: '10px', marginTop: '5px' };
    return (
      <WidgetPanel title="System Stats" helpText={this.helpText}>
        <div style={divStyle}>
          <Segment>
            <Header as='h4' style={headerStyle}>To Date</Header>
            <Statistic.Group widths={3} size="mini" color="blue" items={toDateItems}/>
          </Segment>
        </div>
        <div style={divStyle2}>
          <Segment>
            <Header as='h4' style={headerStyle}>Today</Header>
            <Statistic.Group widths={3} size="mini" color="blue" items={todayItems}/>
          </Segment>
        </div>
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
