import React from 'react';
import Moment from 'moment';
import Calendar from 'react-calendar';
import { Button, Grid, Input, Loader, Popup } from 'semantic-ui-react';
import synchronize from './synchronizer';
import MetricTimeseriesViewer from './MetricTimeseriesViewer';
import WidgetPanel from '../../layouts/WidgetPanel';
import { getLahaStatsInRange } from '../../../api/laha-stats/LahaStatsCollection.methods';


function asEpochS(date) {
    return Math.round(date.getTime() / 1000);
}

class MetricsInspector extends React.Component {
    constructor(props) {
        super(props);

        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - 1); // One day before the end date

        this.state = {
            isLoading: false,
            loaded: false,
            startDate: startDate,
            endDate: endDate,
            startTimestampS: asEpochS(startDate),
            endTimestampS: asEpochS(endDate),
            metrics: [],
            errorReason: null,
        };
        this.dygraphs = [];
    }

    componentDidMount() {
        const { startTimestampS, endTimestampS } = this.state;
        this.retrieveData(startTimestampS, endTimestampS);
    }

    helpText = `
       <p>The Laha Metrics panel displays metrics collected by OPQ Mauka relating to the performance of Mauka and
          the performance of the OPQ system.</p>`;

    /**
     * Render Methods
     */

    render() {
        if (this.state.errorReason) return this.renderError(this.state.errorReason);
        return (!this.state.isLoading) ? this.renderPage() : <Loader active content='Loading...'/>;
    }

    datePicker = () => (
        <Grid.Row><Grid.Column><Grid stackable>
            <Grid.Row>
                <Grid.Column width={6}>
                    <Popup on='focus'
                           trigger={<Input fluid placeholder='Input a starting date' label='Start'
                                           value={Moment(this.state.startDate).format('MM/DD/YYYY')}/>}
                           content={<Calendar onChange={this.changeStartDate} value={this.state.startDate}/>}/>
                </Grid.Column>
                <Grid.Column width={6}>
                    <Popup on='focus'
                           trigger={<Input fluid placeholder='Input an ending date' label='End'
                                           value={Moment(this.state.endDate).format('MM/DD/YYYY')}/>}
                           content={<Calendar onChange={this.changeEndDate} value={this.state.endDate}/>}/>
                </Grid.Column>
                <Grid.Column width={4}>
                    <Button content='Fetch Metrics'
                            fluid
                            onClick={() => this.retrieveData(this.state.startTimestampS, this.state.endTimestampS)}/>
                </Grid.Column>
            </Grid.Row>
        </Grid></Grid.Column></Grid.Row>
    );

    changeStartDate = startDate => { this.setState({ startDate: startDate, startTimestampS: asEpochS(startDate) }); };
    changeEndDate = endDate => { this.setState({ endDate: endDate, endTimestampS: asEpochS(endDate) }); };


    renderPage() {
        const { metrics } = this.state;
        const handleCallback = (dygraph) => {
            this.dygraphs.push(dygraph);
            if (this.dygraphs.length === 18) {
                synchronize(...this.dygraphs);
            }
        };
        return (
            <Grid container stackable>
                <Grid.Column width={16}>
                    <WidgetPanel title='Laha Metrics Viewer' helpText={this.helpText}>
                        <Grid container>
                            {this.datePicker()}
                            {this.state && this.state.loaded &&
                            <Grid.Column width={16}>
                                <MetricTimeseriesViewer
                                    plotTitle={'Active OPQ Boxes'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Active'}
                                    data={this.parseActiveOpqBoxes(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={{}}
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'CPU Usage'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'% CPU'}
                                    data={this.parseCpuPercent(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ { customBars: true } }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Memory Usage'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'MB'}
                                    data={this.parseMemoryMb(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ { customBars: true } }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Disk Usage'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'MB'}
                                    data={this.parseDiskMb(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ { customBars: true } }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Mauka Plugins: Messages Received'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Messages'}
                                    data={this.parseMaukaPluginsMessagesReceived(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'MakaiEventPlugin',
                                            'ThdPlugin',
                                            'StatusPlugin',
                                            'IticPlugin',
                                            'FrequencyVariationPlugin',
                                            'TransientPlugin',
                                            'Ieee1159VoltagePlugin',
                                            'SemiF47Plugin',
                                            'SystemStatsPlugin',
                                            'OutagePlugin',
                                            'LahaGcPlugin',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Mauka Plugins: Messages Published'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Messages'}
                                    data={this.parseMaukaPluginsMessagesPublished(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'MakaiEventPlugin',
                                            'ThdPlugin',
                                            'StatusPlugin',
                                            'IticPlugin',
                                            'FrequencyVariationPlugin',
                                            'TransientPlugin',
                                            'Ieee1159VoltagePlugin',
                                            'SemiF47Plugin',
                                            'SystemStatsPlugin',
                                            'OutagePlugin',
                                            'LahaGcPlugin',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Mauka Plugins: MB Received'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'MB'}
                                    data={this.parseMaukaPluginsMbReceived(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'MakaiEventPlugin',
                                            'ThdPlugin',
                                            'StatusPlugin',
                                            'IticPlugin',
                                            'FrequencyVariationPlugin',
                                            'TransientPlugin',
                                            'Ieee1159VoltagePlugin',
                                            'SemiF47Plugin',
                                            'SystemStatsPlugin',
                                            'OutagePlugin',
                                            'LahaGcPlugin',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Mauka Plugins: MB Published'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'MB'}
                                    data={this.parseMaukaPluginsMbPublished(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'MakaiEventPlugin',
                                            'ThdPlugin',
                                            'StatusPlugin',
                                            'IticPlugin',
                                            'FrequencyVariationPlugin',
                                            'TransientPlugin',
                                            'Ieee1159VoltagePlugin',
                                            'SemiF47Plugin',
                                            'SystemStatsPlugin',
                                            'OutagePlugin',
                                            'LahaGcPlugin',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'GC: Items Garbage Collected'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# GC'}
                                    data={this.parseGcStats(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'samples',
                                            'measurements',
                                            'trends',
                                            'events',
                                            'incidents',
                                            'phenomena',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Collection TTL'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'TTL'}
                                    data={this.parseTtl(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'samples',
                                            'measurements',
                                            'trends',
                                            'events',
                                            'incidents',
                                            'phenomena',
                                        ],
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Instantaneous Measurements Level (Samples)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Samples'}
                                    data={this.parseImlSamples(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Aggregate Measurements Level (Measurements)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Measurements'}
                                    data={this.parseAmlMeasurements(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Aggregate Measurements Level (Trends)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Trends'}
                                    data={this.parseAmlTrends(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Detections Level (Events)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Events'}
                                    data={this.parseDlEvents(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Incidents Level (Incidents)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Incidents'}
                                    data={this.parseIlIncidents(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Laha: Phenomena Level (Phenomena)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'# Phenomena'}
                                    data={this.parsePlPhenomena(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Ground Truth (UHM Meters)'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'Count'}
                                    data={this.parseGroundTruth(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: [
                                            'UTC',
                                            'Count',
                                            'Size MB',
                                        ],
                                        series: {
                                            'Size MB': {
                                                axis: 'y2',
                                            },
                                        },
                                        y2label: 'Size MB',
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Box Triggering Thresholds'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'Thresholds'}
                                    data={this.parseThresholdTriggeringMetrics(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: this.parseThresholdTriggeringLabels(metrics),
                                    } }
                                    height={ '200px' }
                                />
                                <MetricTimeseriesViewer
                                    plotTitle={'Box Measurement Rates'}
                                    xAxisTitle={'UTC'}
                                    yAxisTitle={'Cycles/Measurement'}
                                    data={this.parseMeasurementRateMetrics(metrics)}
                                    dygraphCreatedCallback={handleCallback}
                                    customDygraphOptions={ {
                                        labels: this.parseMeasurementRateLabels(metrics),
                                    } }
                                    height={ '200px' }
                                />
                            </Grid.Column>
                            }
                        </Grid>
                    </WidgetPanel>
                </Grid.Column>
            </Grid>
        );
    }

    /**
     * Helper Methods
     */
    retrieveData(startTimestampS, endTimestampS) {
        this.setState({ loading: true, loaded: false }, () => {
           getLahaStatsInRange.call(
               {
                   startTimestampS: startTimestampS,
                   endTimestampS: endTimestampS,
               },
               (error, metrics) => {
                   this.setState({
                       loading: false,
                       loaded: true,
                       metrics: metrics,
                   });
               },
               );
        });
    }

    triggeringThresholdsBoxSet(metrics) {
        const boxes = new Set();
        for (let i = 0; i < metrics.length; i++) {
            const box_metrics = metrics[i].laha_stats.box_triggering_thresholds;
            for (let j = 0; j < box_metrics.length; j++) {
                boxes.add(box_metrics[j].box_id);
            }
        }
        return boxes;
    }

    measurementRatesBoxSet(metrics) {
        const boxes = new Set();
        for (let i = 0; i < metrics.length; i++) {
            const measurementRates = metrics[i].laha_stats.box_measurement_rates;
            for (let j = 0; j < measurementRates.length; j++) {
                boxes.add(measurementRates[j].box_id);
            }
        }
        return boxes;
    }

    parseThresholdTriggeringMetrics(metrics) {
        function intoSingleSeries(metric, boxes) {
            const series = [];
            const box_metrics = metric.laha_stats.box_triggering_thresholds;
            const boxes_array = Array.from(boxes);
            series.push(metric.timestamp_s);
            for (let i = 0; i < boxes_array.length; i++) {
                const box = boxes_array[i];
                let found = false;
                for (let j = 0; j < box_metrics.length; j++) {
                    const box_metric = box_metrics[j];
                    if (box_metric.box_id === box) {
                        found = true;
                        series.push(box_metric.ref_f);
                        series.push(box_metric.ref_v);
                        series.push(box_metric.threshold_percent_f_low);
                        series.push(box_metric.threshold_percent_f_high);
                        series.push(box_metric.threshold_percent_v_low);
                        series.push(box_metric.threshold_percent_v_high);
                        series.push(box_metric.threshold_percent_thd_high);
                    }
                }
                if (!found) {
                    series.push(null);
                    series.push(null);
                    series.push(null);
                    series.push(null);
                    series.push(null);
                    series.push(null);
                    series.push(null);
                }
            }
            return series;
        }

        function intoSeries(data, boxes) {
            return data.map(function (metric) {
                return intoSingleSeries(metric, boxes);
            });
        }

        const boxes = this.triggeringThresholdsBoxSet(metrics);
        return intoSeries(metrics, boxes);
    }

    parseThresholdTriggeringLabels(metrics) {
        const boxes = this.triggeringThresholdsBoxSet(metrics);
        const graph_labels = [];
        graph_labels.push('timestamp');
        const boxes_array = Array.from(boxes);
        for (let i = 0; i < boxes_array.length; i++) {
            const box = boxes_array[i];
            graph_labels.push(`${box} rF`);
            graph_labels.push(`${box} rV`);
            graph_labels.push(`${box} %Fl`);
            graph_labels.push(`${box} %Fh`);
            graph_labels.push(`${box} %Vl`);
            graph_labels.push(`${box} %Vh`);
            graph_labels.push(`${box} %THDh`);
        }
        return graph_labels;
    }

    parseMeasurementRateMetrics(metrics) {
        function intoSingleSeries(metric, boxes) {
            const series = [];
            const box_measurement_rates = metric.laha_stats.box_measurement_rates;
            const boxes_array = Array.from(boxes);
            series.push(metric.timestamp_s);
            for (let i = 0; i < boxes_array.length; i++) {
                const box = boxes_array[i];
                let found = false;
                for (let j = 0; j < box_measurement_rates.length; j++) {
                    const box_measurement_rate = box_measurement_rates[j];
                    if (box_measurement_rate.box_id === box) {
                        found = true;
                        series.push(box_measurement_rate.measurement_rate);
                    }
                }
                if (!found) {
                    series.push(null);
                }
            }
            return series;
        }

        function intoSeries(data, boxes) {
            return data.map(function (metric) {
                return intoSingleSeries(metric, boxes);
            });
        }

        const boxes = this.measurementRatesBoxSet(metrics);
        return intoSeries(metrics, boxes);
    }

    parseMeasurementRateLabels(metrics) {
        const boxes = this.measurementRatesBoxSet(metrics);
        const graph_labels = [];
        graph_labels.push('timestamp');
        const boxes_array = Array.from(boxes);
        for (let i = 0; i < boxes_array.length; i++) {
            const box = boxes_array[i];
            graph_labels.push(box);
        }
        return graph_labels;
    }

    parseActiveOpqBoxes(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.active_devices]);
    }

    parseCpuPercent(metrics) {
        return metrics.map(metric => [metric.timestamp_s,
            [metric.system_stats.cpu_load_percent.min,
                metric.system_stats.cpu_load_percent.mean,
                metric.system_stats.cpu_load_percent.max]]);
    }

    parseMemoryMb(metrics) {
        return metrics.map(metric => [metric.timestamp_s,
            [metric.system_stats.memory_use_bytes.min / 1000000,
                metric.system_stats.memory_use_bytes.mean / 1000000,
                metric.system_stats.memory_use_bytes.max / 1000000]]);
    }

    parseDiskMb(metrics) {
        return metrics.map(metric => [metric.timestamp_s,
            [metric.system_stats.disk_use_bytes.min / 1000000,
                metric.system_stats.disk_use_bytes.mean / 1000000,
                metric.system_stats.disk_use_bytes.max / 1000000]]);
    }

    parseMaukaPluginsMessagesReceived(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.plugin_stats.MakaiEventPlugin.messages_received,
            metric.plugin_stats.ThdPlugin.messages_received,
            metric.plugin_stats.StatusPlugin.messages_received,
            metric.plugin_stats.IticPlugin.messages_received,
            metric.plugin_stats.FrequencyVariationPlugin.messages_received,
            metric.plugin_stats.TransientPlugin.messages_received,
            metric.plugin_stats.Ieee1159VoltagePlugin.messages_received,
            metric.plugin_stats.SemiF47Plugin.messages_received,
            metric.plugin_stats.SystemStatsPlugin.messages_received,
            metric.plugin_stats.OutagePlugin.messages_received,
            metric.plugin_stats.LahaGcPlugin.messages_received,
        ]);
    }

    parseMaukaPluginsMessagesPublished(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.plugin_stats.MakaiEventPlugin.messages_published,
            metric.plugin_stats.ThdPlugin.messages_published,
            metric.plugin_stats.StatusPlugin.messages_published,
            metric.plugin_stats.IticPlugin.messages_published,
            metric.plugin_stats.FrequencyVariationPlugin.messages_published,
            metric.plugin_stats.TransientPlugin.messages_published,
            metric.plugin_stats.Ieee1159VoltagePlugin.messages_published,
            metric.plugin_stats.SemiF47Plugin.messages_published,
            metric.plugin_stats.SystemStatsPlugin.messages_published,
            metric.plugin_stats.OutagePlugin.messages_published,
            metric.plugin_stats.LahaGcPlugin.messages_published,
        ]);
    }

    parseMaukaPluginsMbReceived(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.plugin_stats.MakaiEventPlugin.bytes_received / 1000000,
            metric.plugin_stats.ThdPlugin.bytes_received / 1000000,
            metric.plugin_stats.StatusPlugin.bytes_received / 1000000,
            metric.plugin_stats.IticPlugin.bytes_received / 1000000,
            metric.plugin_stats.FrequencyVariationPlugin.bytes_received / 1000000,
            metric.plugin_stats.TransientPlugin.bytes_received / 1000000,
            metric.plugin_stats.Ieee1159VoltagePlugin.bytes_received / 1000000,
            metric.plugin_stats.SemiF47Plugin.bytes_received / 1000000,
            metric.plugin_stats.SystemStatsPlugin.bytes_received / 1000000,
            metric.plugin_stats.OutagePlugin.bytes_received / 1000000,
            metric.plugin_stats.LahaGcPlugin.bytes_received / 1000000,
        ]);
    }

    parseMaukaPluginsMbPublished(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.plugin_stats.MakaiEventPlugin.bytes_published / 1000000,
            metric.plugin_stats.ThdPlugin.bytes_published / 1000000,
            metric.plugin_stats.StatusPlugin.bytes_published / 1000000,
            metric.plugin_stats.IticPlugin.bytes_published / 1000000,
            metric.plugin_stats.FrequencyVariationPlugin.bytes_published / 1000000,
            metric.plugin_stats.TransientPlugin.bytes_published / 1000000,
            metric.plugin_stats.Ieee1159VoltagePlugin.bytes_published / 1000000,
            metric.plugin_stats.SemiF47Plugin.bytes_published / 1000000,
            metric.plugin_stats.SystemStatsPlugin.bytes_published / 1000000,
            metric.plugin_stats.OutagePlugin.bytes_published / 1000000,
            metric.plugin_stats.LahaGcPlugin.bytes_published / 1000000,
        ]);
    }

    parseGcStats(metrics) {
        return metrics.map(metric => [
           metric.timestamp_s,
           metric.laha_stats.gc_stats.samples,
           metric.laha_stats.gc_stats.measurements,
           metric.laha_stats.gc_stats.trends,
           metric.laha_stats.gc_stats.events,
           metric.laha_stats.gc_stats.incidents,
           metric.laha_stats.gc_stats.phenomena,
        ]);
    }

    parseTtl(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.instantaneous_measurements_stats.box_samples.ttl,
            metric.laha_stats.aggregate_measurements_stats.measurements.ttl,
            metric.laha_stats.aggregate_measurements_stats.trends.ttl,
            metric.laha_stats.detections_stats.events.ttl,
            metric.laha_stats.incidents_stats.incidents.ttl,
            metric.laha_stats.phenomena_stats.phenomena.ttl,
        ]);
    }

    parseImlSamples(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.instantaneous_measurements_stats.box_samples.count,
            metric.laha_stats.instantaneous_measurements_stats.box_samples.size_bytes / 1000000,
        ]);
    }

    parseAmlMeasurements(metrics) {
        return metrics.map(metric => [
           metric.timestamp_s,
           metric.laha_stats.aggregate_measurements_stats.measurements.count,
           metric.laha_stats.aggregate_measurements_stats.measurements.size_bytes / 1000000,
        ]);
    }

    parseAmlTrends(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.aggregate_measurements_stats.trends.count,
            metric.laha_stats.aggregate_measurements_stats.trends.size_bytes / 1000000,
        ]);
    }

    parseDlEvents(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.detections_stats.events.count,
            metric.laha_stats.detections_stats.events.size_bytes / 1000000,
        ]);
    }

    parseIlIncidents(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.incidents_stats.incidents.count,
            metric.laha_stats.incidents_stats.incidents.size_bytes / 1000000,
        ]);
    }

    parsePlPhenomena(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.laha_stats.phenomena_stats.phenomena.count,
            metric.laha_stats.phenomena_stats.phenomena.size_bytes / 1000000,
        ]);
    }

    parseGroundTruth(metrics) {
        return metrics.map(metric => [
            metric.timestamp_s,
            metric.other_stats.ground_truth.count,
            metric.other_stats.ground_truth.size_bytes / 1000000,
        ]);
    }
}

MetricsInspector.propTypes = { };

export default MetricsInspector;
