import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Button, Grid, Segment, List, Checkbox } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Dygraph from 'dygraphs';
import WidgetPanel from '../../layouts/WidgetPanel';

import { getBoxEvents } from '../../../api/box-events/BoxEventsCollection.methods';
import { getEventData } from '../../../api/fs-files/FSFilesCollection.methods';
import { getEventByEventID } from '../../../api/events/EventsCollection.methods';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';

/** Displays event details, including the waveform at the time of the event. */
class EventOverview extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      event: null,
      boxEvents: [],
      boxIdToWaveformDict: {},
    };
  }

  componentDidMount() {
    const { event_id } = this.props;
    // Retrieve relevant Event and BoxEvents for the given event_id.
    this.retrieveInitialData(event_id);
  }

  /**
   * Render Methods
   */

  render() {
    const { boxEvents } = this.state;
    return this.props.ready && !this.state.isLoading ? (
        <Grid container stackable>
          <Grid.Column width={16}>
            <WidgetPanel title='Event Overview'>
              {this.eventSummary()}
              {boxEvents.map(boxEvent => (
                  this.boxEventSegment(boxEvent)
              ))}
            </WidgetPanel>
          </Grid.Column>
        </Grid>
    ) : '';
  }

  eventSummary() {
    const { event, boxEvents } = this.state;
    const date = event ? Moment(event.target_event_start_timestamp_ms).format('YYYY-MM-DD') : '';
    const time = event ? Moment(event.target_event_start_timestamp_ms).format('HH:mm:ss') : '';
    const duration_ms = event ? event.target_event_end_timestamp_ms - event.target_event_start_timestamp_ms : '';
    let location = '';
    if (event && boxEvents.length) {
      const be = boxEvents.filter(boxEvent => boxEvent.box_id === event.boxes_triggered[0]).shift();
      location = typeof be.location === 'string' ? be.location : be.location[be.location.length - 1].nickname;
    }

    const pStyle = { fontSize: '16px' };

    return event ? (
      <div style={{ marginLeft: '15px' }}>
        <h1>Event Summary</h1>
        <p style={pStyle}>
          An event occurred on <span style={{ backgroundColor: '#b1d4ed' }}>{date} at {time}</span>, lasting for a
          duration of {duration_ms} milliseconds.
        </p>
        <p style={pStyle}>
          The event was initially detected by <span style={{ backgroundColor: '#c3edbb' }}>
          Box {event.boxes_triggered[0]} at {location}</span>, with waveform data available
          for {event.boxes_received.length - 1} other boxes.
        </p>
        <p style={pStyle}>
          The event has been classified as a <span style={{ backgroundColor: '#fcf9a9' }}>{event.type}</span>
        </p>
      </div>
    ) : '';
  }

  boxEventSegment({ event_id, box_id, event_start_timestamp_ms, event_end_timestamp_ms, location }) {
    const { boxIdToWaveformDict } = this.state;
    const waveformVisible = boxIdToWaveformDict[box_id] && boxIdToWaveformDict[box_id].isVisible;
    return (
        <Segment.Group key={box_id} style={{ marginLeft: '15px', marginRight: '15px' }}>
          <Segment.Group horizontal>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hdd outline' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Box ID</List.Header>
                    <List.Description><i>{box_id}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hourglass start' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Start Time</List.Header>
                    <List.Description><i>{Moment(event_start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='hourglass end' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>End Time</List.Header>
                    <List.Description><i>{Moment(event_end_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='clock' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Duration (ms)</List.Header>
                    <List.Description><i>{event_end_timestamp_ms - event_start_timestamp_ms}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <List>
                <List.Item>
                  <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
                  <List.Content style={{ paddingLeft: '2px' }}>
                    <List.Header>Location</List.Header>
                    <List.Description><i>{typeof location === 'string' ? location : location[location.length - 1].nickname}</i></List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Segment>
            <Segment>
              <p style={{ marginBottom: '0px' }}><b>Waveform</b></p>
              <Checkbox toggle onClick={this.toggleWaveform(box_id)} />
            </Segment>
          </Segment.Group>
          {waveformVisible &&
          <Segment>
            <div ref={this.setDygraphRef(box_id)} style={{ width: '100%', height: '200px' }}></div>
          </Segment>
          }
        </Segment.Group>
    );
  }

  /**
   * Event Handlers
   */

  toggleWaveform = (box_id) => () => {
    const { boxIdToWaveformDict } = this.state;
    const boxEntry = boxIdToWaveformDict[box_id];

    // Initial toggle will retrieve waveform data.
    if (!boxEntry) {
      // Set visibility to true so that Segment containing dygraph div is rendered. Then retrieve waveform data.
      this.setState(prevState => {
        const dictClone = { ...prevState.boxIdToWaveformDict };
        dictClone[box_id] = { isVisible: true };
        return {
          boxIdToWaveformDict: dictClone,
        };
      }, () => this.retrieveWaveform(box_id));
    } else {
      // Toggle visibility
      this.setState(prevState => {
        const dictClone = { ...prevState.boxIdToWaveformDict };
        dictClone[box_id].isVisible = !dictClone[box_id].isVisible;
        return {
          boxIdToWaveformDict: dictClone,
        };
      }, () => this.createDygraph(this.getDygraphRef(box_id), boxEntry.dyPlotPoints, boxEntry.dyOptions));
    }
  };

  /**
   * Misc Methods
   */

  retrieveInitialData(event_id) {
    // Given event_id, we'll grab the appropriate Event document, as well as all BoxEvents documents for which data
    // is available (as indicated by Event.boxes_received)
    this.setState({ isLoading: true }, () => {
      getEventByEventID.call({ event_id }, (error, event) => {
        if (error) console.log(error);
        else {
          getBoxEvents.call({ event_id, box_ids: event.boxes_received }, (err, boxEvents) => {
            if (err) console.log(err);
            else {
              this.setState({ boxEvents, event, isLoading: false });
            }
          });
        }
      });
    });
  }

  retrieveWaveform(box_id) {
    const { calibration_constants } = this.props;
    const { boxEvents } = this.state;
    const boxEvent = boxEvents.filter(be => be.box_id === box_id).shift();
    if (!boxEvent) return;

    getEventData.call({ filename: boxEvent.data_fs_filename }, (error, waveform) => {
      if (error) console.log(error);
      else {

        // const dygraphDomElem = this.getDygraphRef(box_id);
        const calibConstant = calibration_constants[box_id] || 1;

        const dyPlotPoints = waveform.map((val, index) => {
          const timestamp = boxEvent.event_start_timestamp_ms + (index * (1.0 / 12.0));
          return [timestamp, val / calibConstant];
        });
        const dyOptions = {
          labels: ['Timestamp', 'Voltage'],
          axes: {
            x: {
              valueFormatter: (millis, opts, seriesName, dygraph, row, col) => { // eslint-disable-line no-unused-vars
                // We must separately calculate the microseconds and concatenate it to the date string.
                const dateString = Moment(millis).format('[[]MM-DD-YYYY[]] HH:mm:ss.SSS').toString()
                    + ((row * (1.0 / 12.0)) % 1).toFixed(3).substring(2);
                return dateString;
              },
              axisLabelFormatter: (timestamp) => Moment(timestamp).format('HH:mm:ss.SSS'),
              pixelsPerLabel: 80,
            },
          },
        };

        this.createDygraph(this.getDygraphRef(box_id), dyPlotPoints, dyOptions);

        // Store plot points and options for the given box_id.
        this.setState(prevState => {
          const updatedDict = { ...prevState.boxIdToWaveformDict };
          updatedDict[box_id] = { ...updatedDict[box_id], dyPlotPoints, dyOptions };
          return {
            boxIdToWaveformDict: updatedDict,
          };
        });
      }
    });
  }

  createDygraph = (dyDomElement, dyPlotPoints, dyPlotOptions) => {
    // Note: There's no real need to store the Dygraph instance itself. It's simpler to allow render() to create a new
    // instance each time the graph visibility is set to true.
    return new Dygraph(dyDomElement, dyPlotPoints, dyPlotOptions);
  };

  /**
   * Ref methods
   * Interacting with non-React third party DOM libraries (such as Dygraph) requires the usage of React Refs.
   * Read more here: https://reactjs.org/docs/refs-and-the-dom.html
   */

  setDygraphRef = box_id => elem => {
    if (elem) this[`dygraph_box_id_${box_id}`] = elem;
  };

  getDygraphRef = box_id => this[`dygraph_box_id_${box_id}`];
}

EventOverview.propTypes = {
  ready: PropTypes.bool.isRequired,
  event_id: PropTypes.number.isRequired,
  calibration_constants: PropTypes.object.isRequired,
};

export default withTracker((props) => {
  const OpqBoxesSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  const opqBoxes = OpqBoxes.find().fetch();

  return {
    ready: OpqBoxesSub.ready(),
    event_id: Number(props.match.params.event_id),
    calibration_constants: opqBoxes.length ? Object.assign(...OpqBoxes.find().fetch().map(box => (
                            { [box.box_id]: box.calibration_constant }
                        ))) : {},
  };
})(EventOverview);
