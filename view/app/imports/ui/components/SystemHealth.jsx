import React from 'react';
import PropTypes from 'prop-types';
import { Label, Loader, Icon } from 'semantic-ui-react';
import { withTracker } from 'meteor/react-meteor-data';
import { Meteor } from 'meteor/meteor';
import WidgetPanel from '../layouts/WidgetPanel';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';

/** Display system statistics. */
class SystemHealth extends React.Component {
  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /**
   * Return a Label indicating the health of the passed Health object.
   * @param health The health object.
   * @returns The Label.
   */
  renderHealth(health, index) {
    return (
        <Label basic key={index} color={health.color}><Icon size="large" name={health.icon}/>{health.name}</Label>
    );
  }

  renderPage() {
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    return (
        <WidgetPanel title="System Health">
          <Label.Group style={divStyle}>
            {this.props.stats && this.props.stats.health.map((health, index) => this.renderHealth(health, index))}
          </Label.Group>
          <p style={divStyle}>This is not functional yet.</p>
        </WidgetPanel>
    );
  }
}

/** Require an array of Stuff documents in the props. */
SystemHealth.propTypes = {
  stats: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const subscription = Meteor.subscribe(SystemStats.getPublicationName());
  return {
    stats: SystemStats.findOne({}),
    ready: subscription.ready(),
  };
})(SystemHealth);
