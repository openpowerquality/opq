import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Header, Statistic, Grid, Segment, Icon, Loader } from 'semantic-ui-react';
import { Trends } from '../../api/trends/TrendsCollection.js';
import { Events } from '../../api/events/EventsCollection.js';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection.js';

class DRS extends React.Component {
  constructor(props) { // eslint-disable-line no-useless-constructor
    super(props);
  }

  listTrends() {
    return this.props.trends.map(trend => <p key={trend._id}>{JSON.stringify(trend, null, 2)}</p>);
  }

  listEvents() {
    return this.props.events.map(event => <p key={event._id}>{JSON.stringify(event, null, 2)}</p>);
  }

  abbreviateNumber(number, numDigitsDisplay = 3) { // eslint-disable-line class-methods-use-this
    const num = Number(number);
    let suffix = '';
    if (num >= 1000 && num < 1000000) suffix = 'K';
    if (num >= 1000000 && num < 1000000000) suffix = 'M';
    if (num >= 1000000000 && num < 1000000000000) suffix = 'B';

    let abbreviatedNumber = num;
    if (num > 999) {
      // Move decimal place as needed. The approach here is to basically modify the number so that it begins with
      // a decimal (eg. 9843 => 0.9843), and then we move the decimal position forward as needed.
      abbreviatedNumber *= 10 ** (numDigitsDisplay - abbreviatedNumber.toString().length);
      abbreviatedNumber = abbreviatedNumber.toFixed(1); // Keep only one decimal place in the end.

      // Then round to whole number.
      abbreviatedNumber = Math.round(abbreviatedNumber);
      const roundedNumDigits = abbreviatedNumber.toString().length;

      // Calculate what 10^pow value we need.
      let pow = null;
      switch (num.toString().length % 3) { // Note that we are checking length of the original given number.
        case 0:
          pow = 3;
          break;
        case 1:
          pow = 1;
          break;
        case 2:
          pow = 2;
          break;
        default:
          break;
      }

      // Finally, move decimal place as needed.
      abbreviatedNumber *= 10 ** (pow - roundedNumDigits);

      // Fix potential floating point rounding issues.
      abbreviatedNumber = abbreviatedNumber.toFixed(roundedNumDigits - pow);
    }

    return `${abbreviatedNumber} ${suffix}`;
  }

  render() {
    const subscriptionsLoaded = this.props.trendsSubscriptionsReady && this.props.eventsSubscriptionsReady
        && this.props.systemStatsSubscriptionsReady;

    if (!subscriptionsLoaded) {
      return <Loader active>Subscriptions Loading...</Loader>;
    } else { // eslint-disable-line no-else-return
      return (
          <Grid stackable padded columns={2}>
            <Grid.Column>
              <Segment attached='top'>
                <Header as='h3'>
                  <Icon name='power' />
                  <Header.Content>
                    System Status
                  </Header.Content>
                </Header>
              </Segment>
              <Segment attached='bottom'>
                <Statistic.Group widths='three' color='blue'>
                  <Statistic>
                    <Statistic.Value>{this.abbreviateNumber(this.props.systemStats.events_count)}</Statistic.Value>
                    <Statistic.Label>Total Events</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.abbreviateNumber(this.props.systemStats.box_events_count)}</Statistic.Value>
                    <Statistic.Label>Total Box Events</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.abbreviateNumber(this.props.systemStats.opq_boxes_count)}</Statistic.Value>
                    <Statistic.Label>Total OPQ Boxes</Statistic.Label>
                  </Statistic>
                </Statistic.Group>

                <Statistic.Group widths='three' color='blue'>
                  <Statistic>
                    <Statistic.Value>
                      {this.abbreviateNumber(this.props.systemStats.measurements_count)}
                    </Statistic.Value>
                    <Statistic.Label>Total Measurements</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.abbreviateNumber(this.props.systemStats.trends_count)}</Statistic.Value>
                    <Statistic.Label>Total Trends</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.abbreviateNumber(this.props.systemStats.users_count)}</Statistic.Value>
                    <Statistic.Label>Total Users</Statistic.Label>
                  </Statistic>
                </Statistic.Group>
              </Segment>

            </Grid.Column>

            <Grid.Column>
              <Segment attached='top'>
                <Header as='h3'>
                  <Icon name='book' />
                  <Header.Content>
                    Pub/Sub Examples
                  </Header.Content>
                </Header>
              </Segment>
              <Segment attached='bottom'>
                <Header as='h3'>Trends Docs Received</Header>
                {this.listTrends()}
                <Header as='h3'>Events Docs Received</Header>
                {this.listEvents()}
              </Segment>
            </Grid.Column>
          </Grid>
      );
    }
  }
}

DRS.propTypes = {
  trends: PropTypes.array,
  trendsSubscriptionsReady: PropTypes.bool,
  events: PropTypes.array,
  eventsSubscriptionsReady: PropTypes.bool,
  systemStats: PropTypes.object,
  systemStatsSubscriptionsReady: PropTypes.bool,
};

export default DRS = withTracker(() => { // eslint-disable-line no-class-assign
  // Lets load 1000 documents so we can demonstrate the loading spinner.
  const trendsSubHandle = Meteor.subscribe(Trends.publicationNames.GET_RECENT_TRENDS, { numTrends: 1000 });
  const trends = Trends.find().fetch();

  const eventsSubHandle = Meteor.subscribe(Events.publicationNames.GET_RECENT_EVENTS, { numEvents: 3 });
  const events = Trends.find().fetch();

  const systemStatsSunHandle = Meteor.subscribe(SystemStats.publicationNames.GET_SYSTEM_STATS);
  const systemStats = SystemStats.findOne();

  return {
    trends,
    trendsSubscriptionsReady: trendsSubHandle.ready(),
    events,
    eventsSubscriptionsReady: eventsSubHandle.ready(),
    systemStats,
    systemStatsSubscriptionsReady: systemStatsSunHandle.ready(),
  };
})(DRS);
