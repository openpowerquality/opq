import React from 'react';
import { Card, Label, Feed } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import Moment from 'moment';

/** Renders a single row in the MyBoxes table. */
class BoxCard extends React.Component {

  renderLocation(location, index) { // eslint-disable-line class-methods-use-this
    const { start_time_ms, zipcode, nickname } = location;
    const timestamp = Moment(start_time_ms).format('MMMM Do YYYY, h:mm a');
    return (
      <Feed.Event key={index}>
        <Feed.Content>
          <Feed.Date>{timestamp}</Feed.Date>
          <Feed.Summary>{nickname} ({zipcode})</Feed.Summary>
        </Feed.Content>
      </Feed.Event>
    );
  }
  render() {
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
      </Card>
    );
  }
}

/** Require a document to be passed to this component. */
BoxCard.propTypes = {
  box: PropTypes.object.isRequired,
};

export default BoxCard;
