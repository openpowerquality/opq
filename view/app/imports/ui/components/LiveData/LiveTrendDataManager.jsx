import React from 'react';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import { Dropdown, Button, Grid } from 'semantic-ui-react';
import Moment from 'moment';

import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import WidgetPanel from '../../layouts/WidgetPanel';
import LiveTrendDataDisplay from './LiveTrendDataDisplay';

class LiveTrendDataManager extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      boxIDs: ['1'],
      length: 'hours',
      measurements: ['voltage'],
    };
  }

  helpText = `
  <p>Live Trends visualizes minute-by-minute summaries of changes in frequency, voltage, or THD for one or more boxes
  over time.</p>
  
  <p>Boxes: select one or more boxes whose values you wish to graph over time. Once you specify a box, you will
  be able to specify whether you want to see its maximum, minimum, and/or average values in its measurements. </p>
  
  <p>Length: Specify how much data you want to see.</p>
  
  <p>Measurements: select voltage, frequency, and/or THD.</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show nothing. */
  render() { return (this.props.ready) ? this.renderPage() : ''; }

  /** Actually renders the page. */
  renderPage() {
    return (
      <WidgetPanel title='Live Trends' helpText={this.helpText}>
        <Grid container>
          <Grid.Column width={16}>
            <Grid stackable>
              <Grid.Column width={7} tablet={6}>
                <Dropdown multiple search selection fluid placeholder='Boxes'
                          options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                          onChange={this.changeBoxes} value={this.state.boxIDs}/>
              </Grid.Column>
              <Grid.Column width={3}>
                <Dropdown search selection fluid placeholder='Length'
                          options={[
                            { text: 'Last hour', value: 'hours' },
                            { text: 'Last day', value: 'days' },
                            { text: 'Last week', value: 'weeks' },
                          ]}
                          onChange={this.changeLength} value={this.state.length}/>
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
            </Grid>
          </Grid.Column>

          {this.state.boxIDs.length > 0 && this.state.measurements.length > 0 && this.state.length ? (
            <Grid.Column width={16}>
              {this.state.measurements.map(measurement => (
                <LiveTrendDataDisplay key={measurement} boxIDs={this.state.boxIDs} measurement={measurement}
                                      timestamp={Moment().subtract(1, this.state.length).valueOf()}
                                      length={this.state.length}/>
              ))}
            </Grid.Column>
          ) : ''}
        </Grid>
      </WidgetPanel>
    );
  }

  changeBoxes = (event, props) => { this.setState({ boxIDs: props.value.sort() }); };
  changeLength = (event, props) => {
    if (this.state.length !== props.value) {
      this.setState({ length: props.value });
    }
  };

  changeMeasurement = (event, props) => {
    let measurements = this.state.measurements;
    const measurement = props.content.toLowerCase();
    if (measurements.includes(measurement)) measurements = measurements.filter(item => item !== measurement);
    else measurements.push(measurement);
    this.setState({ measurements: measurements.sort() });
  };
}


LiveTrendDataManager.propTypes = {
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
})(LiveTrendDataManager);
