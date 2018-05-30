import React from 'react';
import PropTypes from 'prop-types';
import { Segment, Header, Icon, Popup } from 'semantic-ui-react';

/** Provides a standard Panel in which to embed an OPQ UI widget with its title. */
class WidgetPanel extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    const iconStyle = { float: 'right' };
    const noPaddingStyle = (this.props.noPadding) ? { paddingTop: '0px', paddingBottom: '0px' } : {};
    const help = this.props.helpText || 'No help text provided for this widget';
    return (
      <Segment.Group raised>
        <Segment inverted tertiary color="blue">
          <Header as='h5'>
            {this.props.title}
            <Popup trigger={<Icon style={iconStyle} name='question circle' inverted />} on='hover' wide='very'>
              <Popup.Content>
                <div dangerouslySetInnerHTML={{ __html: help }} />
              </Popup.Content>
            </Popup>
          </Header>
        </Segment>
        <Segment vertical attached style={noPaddingStyle}>
          {this.props.children}
        </Segment>
      </Segment.Group>
    );
  }
}

/** Require a title and interior component to be passed in. */
WidgetPanel.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node,
  helpText: PropTypes.string,
  noPadding: PropTypes.bool,
};

export default WidgetPanel;
