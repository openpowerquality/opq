import React from 'react';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import { Loader, Dropdown, Button, Grid } from 'semantic-ui-react';
import Moment from 'moment';

import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import WidgetPanel from '../../layouts/WidgetPanel';
import LiveMeasurementDataDisplay from './LiveMeasurementDataDisplay';

class LiveMeasurementDataManager extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      boxID: '1',
      measurements: ['voltage'],
    };
  }

  helpText = `
  <p>Live Measurements visualizes minute-by-minute summaries of changes in frequency, voltage, or THD for one or more boxes
  over time.</p>
  
  <p>Boxes: select one or more boxes whose values you wish to graph over time. Once you specify a box, you will
  be able to specify whether you want to see its maximum, minimum, and/or average values in its measurements. </p>
  
  <p>Measurements: select voltage, frequency, and/or THD.</p>
  
  <p>This visualization supports panning and zooming.  Scroll the mouse up or down over the visualization to zoom
  in/out of a section. Click and drag right or left to move along the chart.</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() { return (this.props.ready) ? this.renderPage() : <Loader active>Detecting your boxes...</Loader>; }

  /** Actually renders the page. */
  renderPage() {
    return (
      <WidgetPanel title='Live Measurements' helpText={this.helpText}>
        <Grid container stackable>
          <Grid.Row centered>
            <Grid.Column width={7}>
              <Dropdown search selection fluid placeholder='Boxes'
                        options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                        onChange={this.changeBoxes} value={this.state.boxID}/>
            </Grid.Column>
            <Grid.Column width={6}>
              <Button.Group fluid toggle>
                <Button active={this.state.measurements.includes('frequency')} content='Frequency'
                        onClick={this.changeMeasurement}/>
                <Button active={this.state.measurements.includes('thd')} content='THD'
                        onClick={this.changeMeasurement}/>
                <Button active={this.state.measurements.includes('voltage')} content='Voltage'
                        onClick={this.changeMeasurement}/>
              </Button.Group>
            </Grid.Column>
          </Grid.Row>

          {this.state.boxID && this.state.measurements.length > 0 ? (
            <Grid.Column width={16}>
              {this.state.measurements.map(measurement => (
                <LiveMeasurementDataDisplay key={measurement} boxID={this.state.boxID} measurement={measurement}/>
              ))}
            </Grid.Column>
          ) : ''}
        </Grid>
      </WidgetPanel>
    );
  }

  changeBoxes = (event, props) => { this.setState({ boxID: props.value }); };

  changeMeasurement = (event, props) => {
    let measurements = this.state.measurements;
    const measurement = props.content.toLowerCase();
    if (measurements.includes(measurement)) measurements = measurements.filter(item => item !== measurement);
    else measurements.push(measurement);
    this.setState({ measurements: measurements.sort() });
  };
}

/** Require an array of Stuff documents in the props. */
LiveMeasurementDataManager.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const sub = Meteor.subscribe('BoxOwners');
  return {
    ready: sub.ready(),
    boxIDs: Meteor.user() ? BoxOwners.findBoxIdsWithOwner(Meteor.user().username).sort() : undefined,
  };
})(LiveMeasurementDataManager);
