import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Loader } from 'semantic-ui-react';
import MetricTimeseriesViewer from './MetricTimeseriesViewer';
import WidgetPanel from '../../layouts/WidgetPanel';
import { getLahaStatsInRange } from '../../../api/laha-stats/LahaStatsCollection.methods';

class MetricsInspector extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            isLoading: false,
            startTimestampS: props.startTimestampS,
            endTimestampS: props.endTimestampS,
            metrics: [],
            errorReason: null,
        };
    }

    componentDidMount() {
        const { startTimestampS, endTimestampS } = this.state;
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
        this.setState({loading: true}, () => {
           getLahaStatsInRange.call(
               {
                   startTimestampS: startTimestampS,
                   endTimestampS: endTimestampS,
               },
               (error, metrics) => {
                   console.log(startTimestampS, endTimestampS, error, metrics);
                   this.setState({
                       loading: false,
                       metrics: metrics,
                   },
                   () => {})
               })
        });
    }
}

MetricsInspector.propTypes = {
    startTimestampS: PropTypes.number.isRequired,
    endTimestampS: PropTypes.number.isRequired
};

export default withTracker((props) => {
    const { startTimestampS, endTimestampS } = props;
    return {
        startTimestampS: startTimestampS,
        endTimestampS: endTimestampS,
    };
})(MetricsInspector);
