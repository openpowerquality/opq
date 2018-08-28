import React from 'react';
import PropTypes from 'prop-types';
import { Dropdown } from 'semantic-ui-react';

/** Provides a standard Panel in which to embed an OPQ UI widget with its title. */
class BoxSelector extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <Dropdown multiple search selection fluid
                  placeholder='Boxes'
                  options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                  onChange={this.props.onChange}
                  value={this.props.value}
                  style={this.props.style}/>
    );
  }
}

/**
 * When using BoxSelector copy & paste the function below to set as the onChange function
 * and include selectedBoxes in your constructor
 */
// changeSelectedBoxes = (event, data) => {
//   this.setState({ selectedBoxes: data.value.sort() });
// };

/** Require a title and interior component to be passed in. */
BoxSelector.propTypes = {
  boxIDs: PropTypes.array,
  onChange: PropTypes.func,
  value: PropTypes.array,
  style: PropTypes.object,
};

export default BoxSelector;
