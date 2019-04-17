import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Loader } from 'semantic-ui-react';
import MetricTimeseriesViewer from './MetricTimeseriesViewer';
import WidgetPanel from '../../layouts/WidgetPanel';


class MetricsInspector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            startTimestampS: 1555367548,
            endTimestampS: 1555453948,
            errorReason: null,
        };
    }

    componentDidMount() {
        const { startTimestampS, endTimestampS } = this.props;
        // Retrieve relevant Event and BoxEvents for the given event_id.
        this.retrieveInitialData(startTimestampS, endTimestampS);
    }

    helpText = `
       <p>The Laha Metrics panel displays metrics collected by OPQ Mauka relating to the performance of Mauka and
          the performance of the OPQ system.</p>`;

    /**
     * Render Methods
     */

    render() {
        if (this.state.errorReason) return this.renderError(this.state.errorReason);
        return (this.props.ready && !this.state.isLoading) ? this.renderPage() : <Loader active content='Loading...'/>;
    }

    renderPage() {
        return (
            <Grid container stackable>
                <Grid.Column width={16}>
                    <WidgetPanel title='Laha Metrics Viewer' helpText={this.helpText}>
                        <Grid container>
                            <Grid.Column width={12}>
                                <MetricTimeseriesViewer
                                    plotTitle={'Test'}
                                    xAxisTitle={'TestX'}
                                    yAxisTitle={'TestY'}
                                    data={[[0, 1], [1, 2]]}
                                />
                            </Grid.Column>
                        </Grid>
                        <Grid container>
                            <Grid.Column width={12}>
                                <MetricTimeseriesViewer
                                    plotTitle={'Test'}
                                    xAxisTitle={'TestX'}
                                    yAxisTitle={'TestY'}
                                    data={[[0, 1], [1, 2], [2, 3]]}
                                />
                            </Grid.Column>
                        </Grid>
                    </WidgetPanel>
                </Grid.Column>
            </Grid>
        );
    }

    /**
     * Helper Methods
     */
    retrieveInitialData(startTimestampS, endTimestampS) {

    }
}

MetricsInspector.propTypes = {
    ready: PropTypes.bool.isRequired,
    metrics: PropTypes.arrayOf(PropTypes.object),
};

export default withTracker((props) => {
    return {
        ready: true,
        // event_id: Number(props.match.params.event_id),
        // opqBoxes,
        // locations: Locations.find().fetch(),
    };
})(MetricsInspector);
