import React from 'react';
import { Card, Label, Feed, Loader, Header, List } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { withTracker } from 'meteor/react-meteor-data';

/* eslint class-methods-use-this: 0 */

/** Renders a single row in the MyBoxes table. */
class BoxCard extends React.Component {


  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
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

  renderLocations(locations) {
    return (
        <Card.Content extra>
          <Header as='h5'>Locations</Header>
          <List>
            {locations.map((location, index) => this.renderLocation(location, index))}
          </List>
        </Card.Content>
    );
  }

  renderLocation(location, index) {
    const { start_time_ms, zipcode, nickname } = location;
    const timestamp = Moment(start_time_ms).format('MMMM Do YYYY, h:mm a');
    return (
        <List.Item key={index}>
          {nickname} ({zipcode})
          
          Since: {timestamp}
        </List.Item>
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
        {this.renderCalibration(this.props.box.calibration_constant)}
        {this.renderLocations(this.props.box.locations)}
        {this.props.admin ? this.renderOwners(this.props.box.box_id) : ''}
      </Card>
    );
  }
}


BoxCard.propTypes = {
  ready: PropTypes.bool.isRequired,
  box: PropTypes.object.isRequired,
  admin: PropTypes.bool,
};


BoxCard.getDefaultProps = {
  admin: false,
};


/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to box owners in case of Admin access.
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  return {
    ready: boxOwnersSubscription.ready(),
  };
})(BoxCard);

