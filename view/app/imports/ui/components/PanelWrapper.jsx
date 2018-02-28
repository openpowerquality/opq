import React from 'react';
import PropTypes from 'prop-types';
import { Segment, Header, Icon, Button } from 'semantic-ui-react';

class PanelWrapper extends React.Component {
  render() {
    const { headerText, headerIcon, hasButton } = this.props;
    return (
      <div>
        <Segment attached='top'>
          {hasButton &&
            <Button basic icon floated='right' style={{ marginTop: '-6px' }}>
              <Icon name='calendar' /> The Date Here <Icon name='angle down' />
            </Button>
          }

          <div>
            <Header as='h3'>
              <Icon name={headerIcon} />
              <Header.Content>
                {headerText}
              </Header.Content>
            </Header>
          </div>
        </Segment>
        <Segment attached='bottom'>
          {this.props.children}
        </Segment>
      </div>
    );
  }
}

PanelWrapper.propTypes = {
  headerText: PropTypes.string,
  headerIcon: PropTypes.string,
  hasButton: PropTypes.bool,
  children: PropTypes.node,
};

export default PanelWrapper;
