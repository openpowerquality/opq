import React from 'react';
import { Card } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import WidgetPanel from '../layouts/WidgetPanel';
import BoxCard from './BoxCard';

/* eslint max-len:0 */

/** Display the summary information for all Boxes passed in as a property. */
class Boxes extends React.Component {

  /** Render the Boxes as a group of Cards. */
  render() {
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    return (
        <WidgetPanel title={this.props.title}>
          <Card.Group stackable style={divStyle} itemsPerRow={4}>
            {this.props.boxes.map((box) => <BoxCard key={box._id} box={box} admin={this.props.admin} boxTrendStats={this.props.boxTrendStats}/>)}
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
  boxTrendStats: PropTypes.array.isRequired,
};


Boxes.getDefaultProps = {
  admin: false,
};

export default Boxes;
