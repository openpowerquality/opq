import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Header, Statistic, Grid, Segment, Icon, Loader } from 'semantic-ui-react';
import { Trends } from '../../api/trends/TrendsCollection.js';
import { Events } from '../../api/events/EventsCollection.js';
import { totalEventsCount } from '../../api/events/EventsCollectionMethods.js';
import { totalBoxEventsCount } from '../../api/box-events/BoxEventsCollectionMethods.js';
import { totalOpqBoxesCount } from '../../api/opq-boxes/OpqBoxesCollectionMethods.js';
import { totalMeasurementsCount } from '../../api/measurements/MeasurementsCollectionMethods.js';
import { totalTrendsCount } from '../../api/trends/TrendsCollectionMethods.js';
import { totalUsersCount } from '../../api/users/UsersCollectionMethods.js';

class DRS extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      eventsCount: null,
      boxEventsCount: null,
      opqBoxesCount: null,
      measurementsCount: null,
      trendsCount: null,
      usersCount: null,
    };

    // Meteor Method calls. Should this be done in the container?
    totalEventsCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ eventsCount: result });
      }
    });

    totalBoxEventsCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ boxEventsCount: result });
      }
    });

    totalOpqBoxesCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ opqBoxesCount: result });
      }
    });

    totalMeasurementsCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ measurementsCount: result });
      }
    });

    totalTrendsCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ trendsCount: result });
      }
    });

    totalUsersCount.call((error, result) => {
      if (error) {
        console.log(error); // eslint-disable-line no-console
      } else {
        this.setState({ usersCount: result });
      }
    });
  }

  listTrends() {
    return this.props.trends.map(trend => <p key={trend._id}>{JSON.stringify(trend, null, 2)}</p>);
  }

  listEvents() {
    return this.props.events.map(event => <p key={event._id}>{JSON.stringify(event, null, 2)}</p>);
  }

  render() {
    const subscriptionsLoaded = this.props.trendsSubscriptionsReady && this.props.eventsSubscriptionsReady;
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
                    <Statistic.Value>{this.state.eventsCount}</Statistic.Value>
                    <Statistic.Label>Total Events</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.state.boxEventsCount}</Statistic.Value>
                    <Statistic.Label>Total Box Events</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.state.opqBoxesCount}</Statistic.Value>
                    <Statistic.Label>Total OPQ Boxes</Statistic.Label>
                  </Statistic>
                </Statistic.Group>

                <Statistic.Group widths='three' color='blue'>
                  <Statistic>
                    <Statistic.Value>{this.state.measurementsCount}</Statistic.Value>
                    <Statistic.Label>Total Measurements</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.state.trendsCount}</Statistic.Value>
                    <Statistic.Label>Total Trends</Statistic.Label>
                  </Statistic>

                  <Statistic>
                    <Statistic.Value>{this.state.usersCount}</Statistic.Value>
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
};

export default DRS = withTracker(() => { // eslint-disable-line no-class-assign
  // Lets load 1000 documents so we can demonstrate the loading spinner.
  const trendsSubHandle = Meteor.subscribe(Trends.publicationNames.GET_RECENT_TRENDS, { numTrends: 1000 });
  const trends = Trends.find().fetch();

  const eventsSubHandle = Meteor.subscribe(Events.publicationNames.GET_RECENT_EVENTS, { numEvents: 3 });
  const events = Trends.find().fetch();

  return {
    trends,
    trendsSubscriptionsReady: trendsSubHandle.ready(),
    events,
    eventsSubscriptionsReady: eventsSubHandle.ready(),
  };
})(DRS);
