import React from 'react';
import { Loader, Header, Grid } from 'semantic-ui-react';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';
import { LahaConfig } from '../../api/laha-config/LahaConfigCollection';

/**
 * Determines if the ttl values are available.
 * @param props The props that should contain the lahaConfig and ttls values.
 * @returns {boolean} True if the ttls are available, false otherwise.
 */
function hasTtls(props) {
    if (props.lahaConfig === null || props.lahaConfig === undefined || props.lahaConfig.length === 0) {
        return false;
    }

    const lahaConfig = props.lahaConfig[0];
    return !(lahaConfig.ttls === null || lahaConfig.ttls === undefined);
}

/**
 * A recursive function for formatting the TTL to be more human readable.
 * @param ttl The ttl in seconds.
 * @param fmt The already provided format string.
 * @returns {string|(string|string|string)}
 */
function formatTtl(ttl, fmt = '') {
    const secondsInWeek = 604800;
    const secondsInDay = 86400;
    const secondsInHour = 3600;
    const secondsInMinute = 60;

    if (ttl === null || ttl === undefined) {
        return 'n/a';
    }

    if (ttl >= secondsInWeek) {
        return formatTtl(ttl % secondsInWeek, `${fmt}${Math.floor(ttl / secondsInWeek)}w`);
    }
    if (ttl >= secondsInDay) {
        return formatTtl(ttl % secondsInDay, `${fmt}${Math.floor(ttl / secondsInDay)}d`);
    }
    if (ttl >= secondsInHour) {
        return formatTtl(ttl % secondsInHour, `${fmt}${Math.floor(ttl / secondsInHour)}h`);
    }
    if (ttl >= secondsInMinute) {
        return formatTtl(ttl % secondsInMinute, `${fmt}${Math.floor(ttl / secondsInMinute)}m`);
    }
    if (ttl === 0) {
        return fmt;
    }
    return `${fmt}${ttl}s`;
}

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
  <p>System Stats shows descriptive statistics about important entities in this OPQ Cloud instance.</p>
  
  <p>Measurements: Produced once a second by each OPQ Box, these provide instantaneous values for frequency, voltage, 
  and THD.  Measurements are ephemeral and disappear from the database after a period specified as its TTL 
   (Time To Live).</p>
   
   <p>Trends: Produced once per minute, trends indicate the high, low, and average values for 
  frequency, voltage, and THD observed by a single box over a given minute.</p>
  
  <p>Events: Produced whenever an OPQ Box measures frequency, voltage, or THD in excess of a default threshold
  (currently +/- 5% of nominal value.  The creation of an Event normally triggers a request to the OPQ Box to provide
  high fidelity waveform data for the time at which the Event occurred. 
  Events are ephemeral and disappear from the database after a period specified as its TTL (Time To Live).</p>
  
  <p>Incidents: When OPQ Mauka judges that an event has potential significance, it creates an Incident.
   Incidents are ephemeral as well, but typically persist in the database much longer than Events or 
   Measurements.  The exact time is specified by its TTL value. </p>
  
  <p>Phenomena: Represent PQ behaviors that are hypothesized to be regular or predictable based upon lower level
   data including Incidents and Event data.</p>
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
                        <hr/>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        );
    }

    /** Here's the system stats page. */
    renderPage() { // eslint-disable-line class-methods-use-this
        const stat = this.props.stats[0] || {};
        const ttlsExist = hasTtls(this.props);
        const incidentsTtl = ttlsExist ? formatTtl(this.props.lahaConfig[0].ttls.incidents) : 'n/a';
        const eventsTtl = ttlsExist ? formatTtl(this.props.lahaConfig[0].ttls.events) : 'n/a';
        const trendsTtl = ttlsExist ? formatTtl(this.props.lahaConfig[0].ttls.trends) : 'n/a';
        const measurementsTtl = ttlsExist ? formatTtl(this.props.lahaConfig[0].ttls.measurements) : 'n/a';
        const footerStyle = { textAlign: 'center', paddingTop: '10px' };
        return (
            <WidgetPanel title="System Stats" helpText={this.helpText}>
                {this.renderColumnTitles()}
                {this.renderEntity('PHENOMENA', stat.phenomena_count_today, stat.phenomena_count, 'n/a')}
                {
                    this.renderEntity(
                        'INCIDENTS', stat.incidents_count_today, stat.incidents_count,
                        incidentsTtl,
                    )
                }
                {
                    this.renderEntity(
                        'EVENTS', stat.events_count_today, stat.events_count,
                        eventsTtl,
                    )
                }
                {
                    this.renderEntity(
                        'TRENDS', stat.trends_count_today, stat.trends_count,
                        trendsTtl,
                    )
                }
                {
                    this.renderEntity(
                        'MEASUREMENTS', stat.measurements_count_today, stat.measurements_count,
                        measurementsTtl,
                    )
                }
                <p style={footerStyle}>Last update: {Moment(stat.timestamp).format('MMMM Do YYYY, h:mm:ss a')}</p>
            </WidgetPanel>
        );
    }
}

/** Require an array of Stuff documents in the props. */
SystemStatistics.propTypes = {
    stats: PropTypes.array.isRequired,
    lahaConfig: PropTypes.array.isRequired,
    ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
    const subscription = Meteor.subscribe(SystemStats.getPublicationName());
    const lahaConfigSubscription = Meteor.subscribe(LahaConfig.getPublicationName());
    return {
        stats: SystemStats.find({}).fetch(),
        lahaConfig: LahaConfig.find({}).fetch(),
        ready: subscription.ready() && lahaConfigSubscription.ready(),
    };
})(SystemStatistics);
