import React from 'react';
import PropTypes from 'prop-types';
import 'semantic-ui-css/semantic.css';
import { Segment, Header } from 'semantic-ui-react';

/** Provides a standard Panel in which to embed an OPQ UI widget with its title. */
class WidgetPanel extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
      <Segment.Group raised>
        <Segment inverted tertiary color="blue">
          <Header as='h5'>
            {this.props.title}
          </Header>
        </Segment>
        <Segment vertical attached>
          {this.props.children}
        </Segment>
      </Segment.Group>
    );
  }
}

/** Require a title and interior component to be passed in. */
WidgetPanel.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.oneOfType([
    PropTypes.array,
    PropTypes.object,
  ]).isRequired,
};

export default WidgetPanel;
