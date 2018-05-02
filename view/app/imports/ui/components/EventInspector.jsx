import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Popup, Input, Button, Dropdown, Loader } from 'semantic-ui-react';
import Calendar from 'react-calendar';
import Moment from 'moment/moment';

import WidgetPanel from '../layouts/WidgetPanel';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { getEventsInRange } from '../../api/events/EventsCollectionMethods';

/** Displays event details, including the waveform at the time of the event. */
class EventInspector extends React.Component {
  constructor(props) {
    super(props);

    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);

    this.state = {
      start,
      end,
      loading: false,
      events: [],
    };
  }

  helpText = `
  <p>Event Inspector lets you search for an event and look at the details of it, such as the waveform at the time of 
  the event.</p>
  
  <p>Start and End: Select a starting and ending date to search between.</p>
  
  <p>Boxes: select one or more boxes whose events you are interested in.</p>
  
  <p>This visualization supports panning and zooming.  Scroll the mouse up or down over the visualization to change
  the time interval. Click and drag right or left to change the window of time displayed.</p>
  `;

  render() {
    return (
      <WidgetPanel title='Event Inspector'>
        <Grid container>
          <Grid.Column width={16}>
            <Grid stackable>
              <Grid.Row>
                <Grid.Column width={4}>
                  <Popup on='focus'
                         trigger={<Input fluid placeholder='Input a starting date' label='Start'
                                         value={Moment(this.state.start).format('MM/DD/YYYY')}/>}
                         content={<Calendar onChange={this.changeStart} value={this.state.start}/>}/>
                </Grid.Column>
                <Grid.Column width={4}>
                  <Popup on='focus'
                         trigger={<Input fluid placeholder='Input an ending date' label='End'
                                         value={Moment(this.state.end).format('MM/DD/YYYY')}/>}
                         content={<Calendar onChange={this.changeEnd} value={this.state.end}/>}/>
                </Grid.Column>
                <Grid.Column width={5}>
                  <Dropdown multiple search selection fluid
                            placeholder='Boxes to display'
                            options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                            onChange={this.updateBoxIdDropdown}
                            defaultValue={this.state.selectedBoxes}/>
                </Grid.Column>
                <Grid.Column width={3}>
                  <Button content='Search' fluid onClick={this.getEvents}/>
                </Grid.Column>
              </Grid.Row>
              <Grid.Row>
                {this.state.loading ? (
                  <Grid.Column>
                    <Loader active content=' '/>
                  </Grid.Column>
                ) : ''}
              </Grid.Row>
            </Grid>
          </Grid.Column>
        </Grid>
      </WidgetPanel>
    );
  }

  changeStart = start => { this.setState({ start }); };
  changeEnd = end => { this.setState({ end }); };

  getEvents = () => {
    this.setState({ loading: true, () => {

    }});
  };
}

export default withTracker(() => {
  const sub = Meteor.subscribe('opq_boxes');
  return {
    ready: sub.ready(),
    boxIDs: OpqBoxes.find().fetch().map(box => box.box_id).sort(),
  };
})(EventInspector);
