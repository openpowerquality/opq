import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Popup, Input, Button, Dropdown, Loader, Table } from 'semantic-ui-react';
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
    const start = new Date(end);
    start.setDate(end.getDate() - 1);

    this.state = {
      start,
      end,
      loading: false,
      loaded: false,
      selectedBoxes: ['1'],
      events: [],
      test: '',
    };
  }

  helpText = `
  <p>Event Inspector lets you search for an event and look at the details of it, such as the waveform at the time of 
  the event.</p>
  
  <p>Start and End: Select a starting and ending date to search between.</p>
  
  <p>Boxes: select one or more boxes whose events you are interested in.</p>
  `;

  render() {
    return (
      <WidgetPanel title='Event Inspector'>
        <Grid container><Grid.Column width={16}><Grid stackable>
          <Grid.Row>
            <Grid.Column width={5}>
              <Popup on='focus'
                     trigger={<Input fluid placeholder='Input a starting date' label='Start'
                                     value={Moment(this.state.start).format('MM/DD/YYYY HH:mm:ss')}/>}
                     content={<Calendar onChange={this.changeStart} value={this.state.start}/>}/>
              <Input value={this.state.test} error onChange={(event, data) => {
                console.log(this.state.test);
                this.setState({ test: data.value }); }}/>
            </Grid.Column>
            <Grid.Column width={5}>
              <Popup on='focus'
                     trigger={<Input fluid placeholder='Input an ending date' label='End'
                                     value={Moment(this.state.end).format('MM/DD/YYYY HH:mm:ss')}/>}
                     content={<Calendar onChange={this.changeEnd} value={this.state.end}/>}/>
            </Grid.Column>
            <Grid.Column width={4}>
              <Dropdown multiple search selection fluid
                        placeholder='Boxes'
                        options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                        onChange={this.changeSelectedBoxes}
                        defaultValue={this.state.selectedBoxes}/>
            </Grid.Column>
            <Grid.Column width={2}>
              <Button content='Search' fluid onClick={this.getEvents}/>
            </Grid.Column>
          </Grid.Row>
          {this.state.loading ? (
            <Grid.Row>
              <Grid.Column>
                <Loader active content=' '/>
              </Grid.Column>
            </Grid.Row>
          ) : ''}
          {this.state.loaded ? (
            <Grid.Row>
              <Grid.Column width={16}>
                {this.state.events.map(event => (
                  <Table key={event.event_id} celled>
                    <Table.Body>
                      <Table.Row>
                        <Table.Cell>
                          <strong>Event ID:</strong> {event.event_id}
                        </Table.Cell>
                        <Table.Cell>
                          <strong>Type: </strong> {event.type}
                        </Table.Cell>
                        <Table.Cell>
                          <strong>Boxes triggered: </strong> {event.boxes_triggered}
                        </Table.Cell>
                        <Table.Cell>
                          <strong>Started at: </strong>
                          {Moment(event.target_event_start_timestamp_ms).format('MM/DD/YYYY HH:mm:ss')}
                        </Table.Cell>
                        <Table.Cell>
                          <strong>Ended at: </strong>
                          {Moment(event.target_event_end_timestamp_ms).format('MM/DD/YYYY HH:mm:ss')}
                        </Table.Cell>
                      </Table.Row>
                    </Table.Body>
                  </Table>
                ))}
              </Grid.Column>
            </Grid.Row>
          ) : ''}
        </Grid></Grid.Column></Grid>
      </WidgetPanel>
    );
  }

  changeStart = start => { this.setState({ start }); };
  changeEnd = end => { this.setState({ end }); };
  changeSelectedBoxes = (event, data) => { this.setState({ selectedBoxes: data.value }); };

  getEvents = () => {
    const { selectedBoxes, start, end } = this.state;
    this.setState({ loading: true }, () => {
      getEventsInRange.call({ boxIDs: selectedBoxes, startTime_ms: start.getTime(), endTime_ms: end.getTime() },
        (error, events) => {
          this.setState({ events, loading: false, loaded: true });
        });
    });
  };
}

EventInspector.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array,
};

export default withTracker(() => {
  const sub = Meteor.subscribe('opq_boxes');
  return {
    ready: sub.ready(),
    boxIDs: OpqBoxes.find().fetch().map(box => box.box_id).sort(),
  };
})(EventInspector);
