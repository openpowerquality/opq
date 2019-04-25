import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Loader, Segment } from 'semantic-ui-react';
import Dygraph from 'dygraphs';

/** Displays a Waveform graph for the given GridFS filename */
class MetricTimeseriesViewer extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            isLoading: false,
            waveformVisible: true,
            waveformRaw: [],
        };
    }

    componentDidMount() {
        this.createDygraph();
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
                {this.renderWaveformSegment()}
            </Segment.Group>
        );
    }

    renderWaveformSegment() {
        // const { gridfs_filename } = this.props;
        const { waveformVisible, isLoading } = this.state;
        const { height = '150px' } = this.props;

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
                        <div ref={this.setDygraphRef} style={{ width: '100%', height: height }}></div>
                    </Segment>
                </React.Fragment>
                }
            </React.Fragment>
        );
    }


    /**
     * Misc Methods
     */

    createDygraph() {
        const { data, xAxisTitle, yAxisTitle, plotTitle, customDygraphOptions } = this.props;

        // Indicate to the user that their graph is currently being loaded. Dygraphs can take up to a few seconds to
        // load large datasets.
        this.setState({ isLoading: true });


        const dyOptions = {
            labels: [xAxisTitle, yAxisTitle],
            title: plotTitle,
            xlabel: xAxisTitle,
            ylabel: yAxisTitle,
            labelsUTC: true,
            axes: {
                x: {
                    axisLabelFormatter: function (timestamp) {
                        const date = new Date(timestamp * 1000);
                        return `${String(date.getUTCHours()).padStart(2, '0')}\
                         : ${String(date.getUTCMinutes()).padStart(2, '0')}`;
                    },
                },
            },
        };

        const dyDomElement = this.getDygraphRef();
        // Dygraph instantiation is a synchronous operation that can take a few seconds to complete (for large datasets)
        // We defer this operation so that it doesn't hang the client.
        Meteor.defer(() => {
            // Note: There's no real need to store the Dygraph instance itself. It's simpler to allow render() to create
            // a new instance each time the graph visibility is set to true.
            const dygraph = new Dygraph(dyDomElement, data, { ...dyOptions, ...customDygraphOptions });
            dygraph.ready(() => this.setState({ isLoading: false }));
            this.props.dygraphCreatedCallback(dygraph);
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
 * title - The title to display in the header segment. Defaults to 'Waveform Viewer'.
 */
MetricTimeseriesViewer.propTypes = {
    plotTitle: PropTypes.string.isRequired,
    xAxisTitle: PropTypes.string.isRequired,
    yAxisTitle: PropTypes.string.isRequired,
    data: PropTypes.array.isRequired,
    customDygraphOptions: PropTypes.object.isRequired,
    height: PropTypes.string,
    dygraphCreatedCallback: PropTypes.func.isRequired,
};

// Note: This component does not require withTracker(); all the data it requires should be passed in from the parent
// component.
export default MetricTimeseriesViewer;
