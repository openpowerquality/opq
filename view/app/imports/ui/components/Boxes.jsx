import React from 'react';
import { Card } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import WidgetPanel from '../layouts/WidgetPanel';
import BoxCard from './BoxCard';

/** Display user profile info. */
class Boxes extends React.Component {

  /** Here's the system stats page. */
  render() {
    const divStyle = { paddingLeft: '10px' };
    return (
        <WidgetPanel title={this.props.title}>
          <Card.Group stackable style={divStyle}>
            {this.props.boxes.map((box) => <BoxCard key={box._id} box={box} admin={this.props.admin}/>)}
          </Card.Group>
        </WidgetPanel>
    );
  }
}
/** Require an array of Stuff documents in the props. */
Boxes.propTypes = {
  boxes: PropTypes.array.isRequired,
  title: PropTypes.string.isRequired,
  admin: PropTypes.bool,
};


Boxes.getDefaultProps = {
  admin: false,
};

export default Boxes;
