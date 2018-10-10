import React from 'react';
import PropTypes from 'prop-types';
import { Loader, Button, Grid, Segment, List, Checkbox, Popup, Icon } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Dygraph from 'dygraphs';

import { getEventData } from '../../../api/fs-files/FSFilesCollection.methods';

/** Displays BoxEvent details and its corresponding waveform. */
class BoxEventSummary extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      waveformVisible: false,
      waveformRaw: [],
    };
  }

  componentDidUpdate(prevProps, prevState) {
    const { waveformVisible } = this.state;

    // Dygraph requires its target div to be rendered on the DOM before the graph can be created. However, this div is
    // hidden by default (the user must toggle its visibility), which means we must be absolutely sure that the div has
    // been rendered before we attempt to instantiate Dygraph. How do we accomplish this?
    // It works as follows:
    // 1. User hits the waveform toggle button, triggering a setState() in which waveformVisible is set to true.
    // 2. The setState() call triggers a re-render to occur, this time also rendering Dygraph's target div.
    // 3. ComponentDidUpdate() is triggered after the re-render, which notices that waveformVisible has changed to true,
    // subsequently calling the createDygraph() method, which instantiates Dygraph on the now visible div.

    // Create Dygraph instance whenever waveformVisible is changed to true.
    if (waveformVisible && !prevState.waveformVisible) {
      this.createDygraph();
    }
  }

  /**
   * Render Methods
   */

  render() {
    return (!this.state.isLoading) ? this.renderPage() : <Loader active content='Loading...'/>;
  }

  renderPage() {
    const { boxEventDoc, locationDoc } = this.props;
    return this.renderBoxEventSegment(boxEventDoc, locationDoc);
  }

  renderBoxEventSegment({ box_id, event_start_timestamp_ms, event_end_timestamp_ms }, { description }) {
    const { mapZoomCallback } = this.props;
    const { waveformVisible } = this.state;

    return (
        <Segment.Group key={box_id}>
          <Segment style={{ padding: '0px' }}>
            <Grid celled='internally'>
              <Grid.Row>
                <Grid.Column width={2}>
                  <List>
                    <List.Item>
                      <List.Icon name='hdd outline' color='blue' size='large' verticalAlign='middle' />
                      <List.Content style={{ paddingLeft: '2px' }}>
                        <List.Header>Box ID</List.Header>
                        <List.Description><i>{box_id}</i></List.Description>
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>

                <Grid.Column width={3}>
                  <List>
                    <List.Item>
                      <List.Icon name='hourglass start' color='blue' size='large' verticalAlign='middle' />
                      <List.Content style={{ paddingLeft: '2px' }}>
                        <List.Header>Start Time</List.Header>
                        <List.Description>
                          <i>{Moment(event_start_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i>
                        </List.Description>
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>

                <Grid.Column width={3}>
                  <List>
                    <List.Item>
                      <List.Icon name='hourglass end' color='blue' size='large' verticalAlign='middle' />
                      <List.Content style={{ paddingLeft: '2px' }}>
                        <List.Header>End Time</List.Header>
                        <List.Description>
                          <i>{Moment(event_end_timestamp_ms).format('YYYY-MM-DD HH:mm:ss.SSS')}</i>
                        </List.Description>
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>

                <Grid.Column width={3}>
                  <List>
                    <List.Item>
                      <List.Icon name='clock' color='blue' size='large' verticalAlign='middle' />
                      <List.Content style={{ paddingLeft: '2px' }}>
                        <List.Header>Duration (ms)</List.Header>
                        <List.Description><i>{event_end_timestamp_ms - event_start_timestamp_ms}</i></List.Description>
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>

                <Grid.Column width={3}>
                  <List floated='left'>
                    <List.Item>
                      <List.Icon name='marker' color='blue' size='large' verticalAlign='middle' />
                      <List.Content style={{ paddingLeft: '2px' }}>
                        <List.Header>Location</List.Header>
                        <List.Description><i>{description}</i></List.Description>
                      </List.Content>
                    </List.Item>
                  </List>
                  <Popup
                      trigger={
                        <Button icon size='tiny' floated='right' onClick={mapZoomCallback(box_id)}>
                          <Icon size='large' name='crosshairs' />
                        </Button>
                      }
                      content='Zoom to box location'
                  />
                </Grid.Column>

                <Grid.Column width={2}>
                  <p style={{ marginBottom: '0px' }}><b>Waveform</b></p>
                  <Checkbox toggle onClick={this.toggleWaveform} />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Segment>
          {waveformVisible &&
          <Segment>
            <div ref={this.setDygraphRef} style={{ width: '100%', height: '200px' }}></div>
          </Segment>
          }
        </Segment.Group>
    );
  }

  /**
   * Event Handlers
   */

  toggleWaveform = () => {
    const { waveformRaw } = this.state;

    // Retrieve waveform data on initial toggle. Reverse visibility on every subsequent toggle.
    if (!waveformRaw.length) {
      this.retrieveWaveform(); // Note: Sets waveformVisible to true.
    } else {
      // Toggle visibility
      this.setState(prevState => ({ waveformVisible: !prevState.waveformVisible }));
    }
  };

  /**
   * Misc Methods
   */

  retrieveWaveform() {
    const { boxEventDoc } = this.props;

    getEventData.call({ filename: boxEventDoc.data_fs_filename }, (error, waveform) => {
      if (error) console.log(error);
      else {
        this.setState({
          waveformRaw: waveform,
          waveformVisible: true,
        });
      }
    });
  }

  createDygraph() {
    const { boxEventDoc, calibrationConstant = 1 } = this.props;
    const { waveformRaw } = this.state;

    const dyPlotPoints = waveformRaw.map((val, index) => {
      const timestamp = boxEventDoc.event_start_timestamp_ms + (index * (1.0 / 12.0));
      return [timestamp, val / calibrationConstant];
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
          pixelsPerLabel: 90,
        },
      },
    };

    const dyDomElement = this.getDygraphRef();

    // Note: There's no real need to store the Dygraph instance itself. It's simpler to allow render() to create a new
    // instance each time the graph visibility is set to true.
    return new Dygraph(dyDomElement, dyPlotPoints, dyOptions);
  }

  /**
   * Ref methods
   * Interacting with non-React third party DOM libraries (such as Dygraph) requires the usage of React Refs.
   * Read more here: https://reactjs.org/docs/refs-and-the-dom.html
   */

  setDygraphRef = elem => {
    if (elem) this.dygraphElem = elem;
  };

  getDygraphRef = () => this.dygraphElem;
}

BoxEventSummary.propTypes = {
  boxEventDoc: PropTypes.object.isRequired,
  locationDoc: PropTypes.object.isRequired,
  mapZoomCallback: PropTypes.func.isRequired,
  calibrationConstant: PropTypes.number.isRequired,
};

// Note: This component does not require withTracker(); all the data it requires should be passed in from the parent
// component.
export default BoxEventSummary;
