import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Loader, Button, Segment, Checkbox, Popup, Icon, Header } from 'semantic-ui-react';
import Moment from 'moment/moment';
import Dygraph from 'dygraphs';
import { CSVLink } from 'react-csv';

import { getEventData } from '../../api/fs-files/FSFilesCollection.methods';

/** Displays a Waveform graph for the given GridFS filename */
class WaveformViewer extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoading: false,
      waveformVisible: false,
      waveformRaw: [],
    };
  }

  componentDidMount() {
    const { displayOnLoad } = this.props;

    if (displayOnLoad) this.toggleWaveform();
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
    return this.renderWaveformViewer();
  }

  renderWaveformViewer() {
    return (
        <Segment.Group>
          {this.renderTopSegment()}
          {this.renderWaveformSegment()}
        </Segment.Group>
    );
  }

  renderTopSegment() {
    const { waveformVisible } = this.state;

    return (
        <Segment clearing>
          <div style={{ float: 'right' }}>
            <p style={{
              display: 'inline-block',
              verticalAlign: 'top',
              marginBottom: '0px',
              marginRight: '10px' }}>
                <b>Toggle Waveform</b>
            </p>
            <Checkbox toggle checked={waveformVisible} onClick={this.toggleWaveform} />
          </div>
          <Header size='medium' floated='left'>
            Waveform Viewer
          </Header>
        </Segment>
    );
  }

  renderWaveformSegment() {
    const { gridfs_filename } = this.props;
    const { waveformVisible, isLoading } = this.state;

    return (
        <React.Fragment>
          {isLoading && !waveformVisible &&
          <Segment>
            <Loader active content='Downloading waveform data...'/>
          </Segment>
          }
          {waveformVisible &&
          <React.Fragment>
            <Segment>
              {isLoading &&
              <Loader active content='Loading waveform...'/>
              }
              <div ref={this.setDygraphRef} style={{ width: '100%', height: '200px' }}></div>
            </Segment>
            <Segment>
              <Popup
                  trigger={
                    <Button as={CSVLink}
                            icon
                            color='blue'
                            filename={`${gridfs_filename}.csv`}
                            data={this.getCalibratedWaveformCSV()}>
                      <Icon size='large' name='download' />
                      <span style={{ marginLeft: '3px', verticalAlign: 'middle' }}>Download CSV</span>
                    </Button>
                  }
                  content='Download CSV'
              />
            </Segment>
          </React.Fragment>
          }
        </React.Fragment>
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
    const { gridfs_filename } = this.props;

    this.setState({ isLoading: true }, () => {
      getEventData.call({ filename: gridfs_filename }, (error, waveform) => {
        if (error) console.log(error);
        else {
          this.setState({
            waveformRaw: waveform,
            waveformVisible: true,
            isLoading: false,
          });
        }
      });
    });
  }

  getCalibratedWaveformCSV = () => {
    const { opqBoxDoc } = this.props;
    const { waveformRaw } = this.state;
    if (waveformRaw.length) {
      return waveformRaw.map(val => [val / opqBoxDoc.calibration_constant]);
    }
    return null;
  };

  createDygraph() {
    const { startTimeMs, opqBoxDoc } = this.props;
    const { waveformRaw } = this.state;

    // Indicate to the user that their graph is currently being loaded. Dygraphs can take up to a few seconds to load
    // large datasets.
    this.setState({ isLoading: true });

    const boxCalibConst = opqBoxDoc.calibration_constant || 1;
    const SAMPLES_PER_CYCLE = 200;
    const waveformCalibrated = waveformRaw.map(val => val / boxCalibConst);
    const dyPlotPoints = waveformCalibrated.map((val, idx) => {
      const timestamp = startTimeMs + (idx * (1.0 / 12.0));

      // Calculate RMS of last 200 points (1 cycle).
      let squaredSum = 0;
      for (let i = 0; i < SAMPLES_PER_CYCLE && idx - i > -1; i++) {
        squaredSum += waveformCalibrated[idx - i] ** 2;
      }
      // For the first 200 values, we must divide by the current index for our RMS calculation.
      const divisor = (idx < SAMPLES_PER_CYCLE) ? idx + 1 : SAMPLES_PER_CYCLE;
      const rms = Math.sqrt(squaredSum / divisor);
      return [timestamp, val, rms];
    });

    const dyOptions = {
      labels: ['Timestamp', 'Voltage', 'RMS'],
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
    // Dygraph instantiation is a synchronous operation that can take a few seconds to complete (for large datasets).
    // We defer this operation so that it doesn't hang the client.
    Meteor.defer(() => {
      // Note: There's no real need to store the Dygraph instance itself. It's simpler to allow render() to create a new
      // instance each time the graph visibility is set to true.
      const dygraph = new Dygraph(dyDomElement, dyPlotPoints, dyOptions);
      dygraph.ready(() => this.setState({ isLoading: false }));
    });
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

/**
 * WaveformViewer Component Props
 *
 * gridfs_filename - The GridFS filename of the waveform to display.
 * opqBoxDoc - The OpqBox document associated with the waveform.
 * startTimeMs - The starting time to display for the waveform graph, in milliseconds since epoch.
 * displayOnLoad - Enables automatic download and display of waveform graph once the component is mounted.
 */
WaveformViewer.propTypes = {
  gridfs_filename: PropTypes.string.isRequired,
  opqBoxDoc: PropTypes.object.isRequired,
  startTimeMs: PropTypes.number.isRequired,
  displayOnLoad: PropTypes.bool,
};

// Note: This component does not require withTracker(); all the data it requires should be passed in from the parent
// component.
export default WaveformViewer;
