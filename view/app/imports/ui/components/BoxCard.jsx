import React from 'react';
import { Card, Label, Feed, Loader } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import Moment from 'moment';
import { Meteor } from 'meteor/meteor';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { withTracker } from 'meteor/react-meteor-data';
import Boxes from './Boxes';

/** Renders a single row in the MyBoxes table. */
class BoxCard extends React.Component {


  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /**
   * Return a feed event for each location entry.
   * @param location The location entry.
   * @param index An index, to be used as the key.
   * @returns {*} The Feed.Event.
   */
  renderLocation(location, index) { // eslint-disable-line class-methods-use-this
    const { start_time_ms, zipcode, nickname } = location;
    const timestamp = Moment(start_time_ms).format('MMMM Do YYYY, h:mm a');
    return (
      <Feed.Event key={index}>
        <Feed.Content>
          <Feed.Date>Since: {timestamp}</Feed.Date>
          <Feed.Summary>{nickname} ({zipcode})</Feed.Summary>
        </Feed.Content>
      </Feed.Event>
    );
  }

  renderOwners(boxId) { // eslint-disable-line class-methods-use-this
    const owners = BoxOwners.findOwnersWithBoxId(boxId);
    return (
      <Card.Content>
        Owners: {owners.map(owner => `${owner}, `)}
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
          <Card.Meta>{this.props.box.description}</Card.Meta>
        </Card.Content>
        <Card.Content extra>
          Calibration: {this.props.box.calibration_constant}
        </Card.Content>
        <Card.Content extra>
          <Feed>
            {this.props.box.locations.map((location, index) => this.renderLocation(location, index))}
          </Feed>
        </Card.Content>
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

