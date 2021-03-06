import React from 'react';
import { Card, Label, Loader, Header, List, Icon } from 'semantic-ui-react';
import { withRouter } from 'react-router-dom';
import PropTypes from 'prop-types';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';

/* eslint class-methods-use-this: 0 */

/** Renders a single row in the MyBoxes table. */
class BoxCard extends React.Component {


  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  renderOwners(boxId) {
    const owners = BoxOwners.findOwnersWithBoxId(boxId);
    return (
      <Card.Content extra>
        <Header as='h5'>Owners</Header>
        <List>
          {owners.map((owner, index) => (<List.Item key={index}>{owner}</List.Item>))}
        </List>
      </Card.Content>
    );
  }

  renderDescription(description) {
    return (
        <Card.Content extra>
          <Header as='h5'>Description</Header>
          {description}
        </Card.Content>
    );
  }

  renderCalibration(calibration) {
    return (
        <Card.Content extra>
          <Header as='h5'>Calibration Constant</Header>
          {calibration}
        </Card.Content>
    );
  }

  renderCurrentLocation(locationSlug, location_start_time_ms) {
    const locationString = Locations.getDoc(locationSlug).description;
    const timeString = (location_start_time_ms) ? Moment(location_start_time_ms).format('lll') : 'N/A';
    return (
      <Card.Content extra>
        <Header as='h5'>Current Location</Header>
        <List>
          <List.Item key={1}>{ locationString }</List.Item>
          <List.Item key={2}>Since: { timeString }</List.Item>
        </List>
      </Card.Content>
    );
  }

  renderArchivedLocations(locationArchive) {
    return (
      <Card.Content extra>
        <Header as='h5'>Archived Locations</Header>
        <List>
          {locationArchive && locationArchive.map((location, index) => this.renderArchivedLocation(location, index))}
        </List>
      </Card.Content>
    );
  }

  renderArchivedLocation(archivedLocation, index) {
    const { location_start_time_ms, location } = archivedLocation;
    const timestamp = (location_start_time_ms) ? Moment(location_start_time_ms).format('lll') : 'N/A';
    return (
      <List.Item key={index}>
        <p>{ location }</p>
        Since: { timestamp }
      </List.Item>
    );
  }

  renderBoxTrendStats(boxId, boxTrendStats) {
    const boxTrends = _.find(boxTrendStats, stat => stat.boxId === boxId);
    const first = boxTrends && boxTrends.firstTrend ? Moment(boxTrends.firstTrend).format('lll') : 'N/A';
    const last = boxTrends && boxTrends.lastTrend ? Moment(boxTrends.lastTrend).format('lll') : 'N/A';
    const total = boxTrends && boxTrends.totalTrends ? boxTrends.totalTrends : 0;
    const totalDays = (total / (60 * 24)).toFixed(0);
    return (
      <Card.Content>
        <Header as='h5'>Trend Statistics</Header>
        <List>
          <List.Item>First: {first}</List.Item>
          <List.Item>Last: {last}</List.Item>
          <List.Item>Days Worth of Data: {totalDays}</List.Item>
        </List>
      </Card.Content>
    );
  }

  renderStatus(boxId, unplugged, boxTrendStats) {
    const boxTrends = _.find(boxTrendStats, stat => stat.boxId === boxId);
    const last = boxTrends && boxTrends.lastTrend ? Moment(boxTrends.lastTrend) : undefined;
    const diffMinutes = last && Moment().diff(last, 'minutes');
    let status = 'Unknown';
    let color = 'grey';
    let icon = 'question';
    if (diffMinutes) {
      if (diffMinutes > 5) {
        status = 'Offline';
        color = 'red';
        icon = 'exclamation';
      } else {
        status = 'Online';
        color = 'green';
        icon = 'star';
      }
    }
    if (unplugged) {
      status = 'Unplugged';
      color = 'orange';
      icon = 'plug';
    }
    return (
      <Card.Content>
        <Header as='h5'>Status</Header>
        <Label color={color}><Icon name={icon} /> {status}</Label>
      </Card.Content>
    );
  }

  /**
   * Render a Card corresponding to each Box.
   * @returns The Card.
   */
  renderPage() {
    return (
      <Card>
        <Card.Content>
          <Label corner='right' circular color='blue'>{this.props.box.box_id}</Label>
          <Card.Header>{this.props.box.name}</Card.Header>
        </Card.Content>
        {this.renderDescription(this.props.box.description)}
        {/* this.renderStatus(this.props.box.box_id, this.props.box.unplugged, this.props.boxTrendStats) */}
        {this.renderCalibration(this.props.box.calibration_constant)}
        {this.renderCurrentLocation(this.props.box.location, this.props.box.location_start_time_ms)}
        {this.renderArchivedLocations(this.props.box.location_archive)}
        {this.renderBoxTrendStats(this.props.box.box_id, this.props.boxTrendStats)}
        {this.props.admin ? this.renderOwners(this.props.box.box_id) : ''}
      </Card>
    );
  }
}

/*
  <Card.Content extra>
     <Link to={`/edit/${this.props.box.box_id}`}>Edit</Link>
   </Card.Content>
*/


BoxCard.propTypes = {
  ready: PropTypes.bool.isRequired,
  box: PropTypes.object.isRequired,
  boxTrendStats: PropTypes.array.isRequired,
  admin: PropTypes.bool,
};


BoxCard.getDefaultProps = {
  admin: false,
};


/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to box owners in case of Admin access.
  const boxOwnersSub = Meteor.subscribe(BoxOwners.getPublicationName());
  const locationsSub = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: boxOwnersSub.ready() && locationsSub.ready(),
  };
})(withRouter(BoxCard));

