import React from 'react';
import PropTypes from 'prop-types';
import { Label, Loader, Icon } from 'semantic-ui-react';
import { withTracker } from 'meteor/react-meteor-data';
import { Meteor } from 'meteor/meteor';
import WidgetPanel from '../layouts/WidgetPanel';
import { SystemStats } from '../../api/system-stats/SystemStatsCollection';
import { Healths } from '../../api/health/HealthsCollection';

/** Display system statistics. */
class SystemHealth extends React.Component {

  helpText = `
  <p>System Health provides a visual indication of the current status of OPQ services and boxes. </p>
  
  <p>Services can either be 'up' (green) or 'down' (red). All services should always be up.</p>
  
  <p>Boxes can be 'up' (green), 'down' (red), or 'unplugged' (grey).  When a user wants a box to be registered
  in the system but isn't using it currently, they can set its status to unplugged to indicate that the lack
  of data transmission is not an indication of system malfunction. </p>
  
  <p>This data is provided by the OPQ Health component.</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
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
    console.log(this.props.healths);
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    const headerStyle =
      { paddingLeft: '10px', paddingRight: '10px', textAlign: 'center', fontWeight: 'bold', marginBottom: '5px' };
    const services = this.props.stats.health.filter(health => health.type === 'service');
    const boxes = this.props.stats.health.filter(health => health.type === 'box');
    return (
        <WidgetPanel title="System Health" helpText={this.helpText}>
          <p style={headerStyle}>Services</p>
          <Label.Group style={divStyle}>
            {services.map((health, index) => this.renderHealth(health, index))}
          </Label.Group>
          <p style={headerStyle}>OPQ Boxes</p>
          <Label.Group style={divStyle}>
            {boxes.map((health, index) => this.renderHealth(health, index))}
          </Label.Group>
        </WidgetPanel>
    );
  }
}

/** Require an array of Stuff documents in the props. */
SystemHealth.propTypes = {
  stats: PropTypes.object,
  healths: PropTypes.array,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const subscription = Meteor.subscribe(SystemStats.getPublicationName());
  const subscription2 = Meteor.subscribe(Healths.getPublicationName());
  return {
    stats: SystemStats.findOne({}),
    healths:
      Healths.find({ timestamp: { $gt: new Date(Date.now() - (1000 * 62)) } }, { sort: { timestamp: -1 } }).fetch(),
    ready: subscription.ready() && subscription2.ready(),
  };
})(SystemHealth);
