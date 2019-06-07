import React from 'react';
import PropTypes from 'prop-types';
import { Label, Loader, Icon } from 'semantic-ui-react';
import { withTracker } from 'meteor/react-meteor-data';
import { Meteor } from 'meteor/meteor';
import Moment from 'moment/moment';
import WidgetPanel from '../layouts/WidgetPanel';
import { Healths } from '../../api/health/HealthsCollection';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';


/** Display system statistics. */
class SystemHealth extends React.Component {

  helpText = `
  <p>System Health provides a visual indication of the current status of OPQ services and boxes. </p>
  
  <p>Services can either be 'up' (green), 'down' (red), or 'unknown' (grey). All services should always be up.</p>
  
  <p>Boxes can be 'up' (green), 'down' (red), 'unknown' (grey), or 'unplugged' (yellow).  
  When a user wants a box to be registered
  in the system but isn't using it currently, they can set its status to unplugged to indicate that the lack
  of data transmission is not an indication of system malfunction. Boxes should always be 'up' or 'unplugged'. </p>
  
  <p>This data is provided by the OPQ Health middleware service. 'Unknown' means that the Health service has not
  reported a value for this service or box in the last minute.</p>
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

  /**
   * Return an object indicating the status of the supplied middleware service.
   * @param healths An array of recent health documents.
   * @param service The service of interest
   * @returns { Object } Indicates health of service: up, down, or unknown
   */
  serviceHealthStatus(healths, service) {
    const healthDoc = _.find(healths, health => health.service === service);
    const name = service.toLowerCase();
    // If no record, return unknown (grey)
    if (!healthDoc) {
      return { name, color: 'grey', icon: 'question circle' };
    }
    // If up, return green.
    if (healthDoc.status === 'UP') {
      return { name, color: 'green', icon: 'check circle' };
    }
    // Otherwise assume down, return red.
    return { name, color: 'red', icon: 'exclamation circle' };
  }

  /**
   * Return an object indicating the status of the supplied boxID.
   * @param healths An array of recent health documents.
   * @param boxID The box of interest
   * @returns { Object } Indicates health of box: up, down, unknown, or unplugged.
   */
  boxHealthStatus(healths, boxID) {
    const healthDoc = _.find(healths, health => (health.service === 'BOX' && health.serviceID === boxID));
    const boxDoc = _.find(this.props.boxes, doc => doc.box_id === boxID);
    const name = `Box ${boxID}`;
    // If unplugged, return unplugged
    if (boxDoc && boxDoc.unplugged) {
      return { name, color: 'yellow', icon: 'plug' };
    }
    // If no record, return unknown (grey)
    if (!healthDoc) {
      return { name, color: 'grey', icon: 'question circle' };
    }
    // If up, return green.
    if (healthDoc.status === 'UP') {
      return { name, color: 'green', icon: 'check circle' };
    }
    // Otherwise assume down, return red.
    return { name, color: 'red', icon: 'exclamation circle' };
  }

  /**
   * RenderPage shows the status.
   * Each entity can be in state "up", "down", or "unknown" (if Health does not report on them.)
   * Boxes can also be in state "unplugged".
   * Last update time: from the first record.
   * Must update Health documentation to say that this component expects reporting at least once a minute.
   * For the four services, can just _.find to get the first record.
   * For the boxes, must subscribe to OPQBoxes to generate the list of box IDs. Then generate an array of results.
   * @returns {*}
   */
  renderPage() {
    const services = ['MAUKA', 'MAKAI', 'MONGO', 'HEALTH'];
    const boxIDs = this.props.boxes.map(box => box.box_id).sort();
    const serviceHealth = _.map(services, service => this.serviceHealthStatus(this.props.healths, service));
    const boxHealth = _.map(boxIDs, id => this.boxHealthStatus(this.props.healths, id));
    const lastUpdate = this.props.healths[0] ?
      Moment(this.props.healths[0].timestamp).format('MMMM Do YYYY, h:mm:ss a') : 'Unknown';

    const footerStyle = { textAlign: 'center', paddingTop: '10px' };
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    const headerStyle =
      { paddingLeft: '10px', paddingRight: '10px', textAlign: 'center', fontWeight: 'bold', marginBottom: '5px' };
    return (
        <WidgetPanel title="System Health" helpText={this.helpText}>
          <p style={headerStyle}>Services</p>
          <Label.Group style={divStyle}>
            {serviceHealth.map((health, index) => this.renderHealth(health, index))}
          </Label.Group>
          <p style={headerStyle}>OPQ Boxes</p>
          <Label.Group style={divStyle}>
            {boxHealth.map((health, index) => this.renderHealth(health, index))}
          </Label.Group>
          <p style={footerStyle}>Last update: {lastUpdate}</p>
        </WidgetPanel>
    );
  }
}

/** Require an array of Stuff documents in the props. */
SystemHealth.propTypes = {
  healths: PropTypes.array,
  boxes: PropTypes.array,
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Calculate a timestamp for two minutes ago exactly on the minute.
  // This ensures that we won't get an excessive number of Health documents.
  // Note: Can't just calculate the current time in milliseconds, since value changes every millisecond, creating
  // an infinite loop! That's a day of debugging I will never get back.
  const startTime = Moment().seconds(0).milliseconds(0).subtract(2, 'minutes').toDate();
  const healthsSub = Meteor.subscribe(Healths.getPublicationName(), { startTime });
  const opqBoxesSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    ready: healthsSub.ready() && opqBoxesSub.ready(),
    healths:
      Healths.find({ timestamp: { $gt: startTime } }, { sort: { timestamp: -1 } }).fetch(),
    boxes: OpqBoxes.find().fetch(),
    boxIDs: OpqBoxes.find().fetch().map(box => box.box_id).sort(),
  };
})(SystemHealth);
