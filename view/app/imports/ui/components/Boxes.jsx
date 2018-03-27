import React from 'react';
import { Card } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import WidgetPanel from '../layouts/WidgetPanel';
import BoxCard from './BoxCard';

/** Display user profile info. */
class Boxes extends React.Component {

  /** Here's the system stats page. */
  render() {
    return (
        <WidgetPanel title={this.props.title}>
          <Card.Group stackable>
            {this.props.boxes.map((box) => <BoxCard key={box._id} box={box} />)}
          </Card.Group>
        </WidgetPanel>
    );
  }
}
/** Require an array of Stuff documents in the props. */
Boxes.propTypes = {
  boxes: PropTypes.array.isRequired,
  title: PropTypes.string.isRequired
};

export default Boxes;
