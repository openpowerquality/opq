import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import Moment from 'moment';
import {
  Charts, ChartContainer, ChartRow, YAxis, LineChart, Baseline, Resizable, Legend, styler,
} from 'react-timeseries-charts';
import { TimeRange, TimeSeries } from 'pondjs';

import { Trends } from '../../../api/trends/TrendsCollection';

import colors from '../../utils/colors';

class LiveTrendDataManager extends React.Component {
  /** Initializes the state of this component. It cannot be done in a constructor because the state
   * _always_ depends on the props passed by LiveTrendDataManager. */
  componentDidMount() {
    const linesToShow = [];
    const disabled = {};
    this.props.boxIDs.forEach(boxID => {
      linesToShow.push(`Box ${boxID} avg`); disabled[`Box ${boxID} avg`] = false;
      linesToShow.push(`Box ${boxID} max`); disabled[`Box ${boxID} max`] = false;
      linesToShow.push(`Box ${boxID} min`); disabled[`Box ${boxID} min`] = false;
    });

    const lineColors = {};
    let colorCounter = 0;
    linesToShow.forEach(label => {
      lineColors[label] = colors[colorCounter++];
    });

    this.setState({
      linesToShow,
      disabled,
      lineColors,
      timeRange: this.props.timeRange,
      length: this.props.length,
      colorCounter,
    });
  }

  /** Updates the state based on changes to props. */
  componentWillReceiveProps(nextProps){
    if (nextProps.length !== this.state.length) this.setState({
      timeRange: nextProps.timeRange,
      length: nextProps.length,
    });
    else if (nextProps.trendData !== this.props.trendData) {
      const diff = nextProps.start - this.props.start;
      const range = [this.state.timeRange.begin().valueOf() + diff, this.state.timeRange.end().valueOf() + diff];
      this.setState({ timeRange: new TimeRange(range) });
    }

    if (nextProps.boxIDs !== this.props.boxIDs) {
      const linesToShow = [];
      const disabled = this.state.disabled;
      nextProps.boxIDs.forEach(boxID => {
        linesToShow.push(`Box ${boxID} avg`);
        if (disabled[`Box ${boxID} avg`] === undefined) disabled[`Box ${boxID} avg`] = false;
        linesToShow.push(`Box ${boxID} max`);
        if (disabled[`Box ${boxID} max`] === undefined) disabled[`Box ${boxID} max`] = false;
        linesToShow.push(`Box ${boxID} min`);
        if (disabled[`Box ${boxID} min`] === undefined) disabled[`Box ${boxID} min`] = false;
      });
      let colorCounter = 0;
      const lineColors = {};
      linesToShow.forEach(label => {
        lineColors[label] = colors[colorCounter++];
      });
      this.setState({
        linesToShow: linesToShow.sort(),
        disabled,
        lineColors,
        colorCounter,
      });
    }
  }

  render() {
    return this.props.ready ? this.renderPage() : '';
  }

  renderPage = () => {
    return (
      this.generateGraph(this.props.measurement)
    );
  };


/** Doing it this way instead of putting code directly in renderPage(), so that it is easier to see the parallels
 * between the other similar components */
  generateGraph = (measurement) => {
    // @formatter:off
    let headerContent = '';
    switch (measurement) {
      case 'frequency': headerContent = 'Frequency'; break;
      case 'thd': headerContent = 'THD'; break;
      case 'voltage': headerContent = 'Voltage'; break;
      default: break;
    }
    // @formatter:on

    const legend = this.state.linesToShow.map(label => ({ key: label, label, disabled: this.state.disabled[label] }));
    const legendStyle = styler(this.state.linesToShow.map(label => (
      { key: label, color: this.state.lineColors[label] })));

    const graphData = this.getGraphData(measurement);
    const reference = this.generateReference(measurement);
    const wholeDataSet = [];
    graphData.forEach(set => { set.data.forEach(point => { wholeDataSet.push(point[1]); }); });
    reference.forEach(value => { wholeDataSet.push(value); });

    return (
      <div>
        <Legend type='swatch' align='left' categories={legend} style={legendStyle}
                onSelectionChange={this.legendClicked}/>
        <Resizable>
          <ChartContainer timeRange={this.state.timeRange} enablePanZoom minDuration={60000 * 3}
                          onTimeRangeChanged={timeRange => this.setState({ timeRange })}
                          minTime={new Date(this.props.start)} maxTime={new Date(this.props.end)}>
            <ChartRow height={100}>
              <YAxis id={measurement} format={n => n.toFixed(2)} label={headerContent} labelOffset={-10} width={60}
                     min={Math.min(...wholeDataSet)} max={Math.max(...wholeDataSet)} />
              <Charts>
                {graphData.map(set => {
                  const series = new TimeSeries({
                    name: set.label,
                    columns: ['time', 'value'],
                    points: set.data,
                  });
                  const style = { value: { normal: { stroke: this.state.lineColors[set.label], strokeWidth: 2 } } };
                  return <LineChart key={set.label} axis={measurement} series={series} style={style}/>;
                })}
                <Baseline axis={measurement} style={{ line: { stroke: 'grey' } }}
                          value={reference[1]} label='Nominal' position='right'/>
                <Baseline axis={measurement} style={{ line: { stroke: 'lightgrey' } }}
                          value={reference[2]} label='+5%' position='right'/>
                <Baseline axis={measurement} style={{ line: { stroke: 'lightgrey' } }}
                          value={reference[0]} label='-5%' position='right' visible={measurement !== 'thd'}/>
              </Charts>
            </ChartRow>
          </ChartContainer>
        </Resizable>
      </div>
    );
  };

  getGraphData = measurement => {
    const trendData = this.props.trendData;
    const linesToShow = this.state.linesToShow;
    return linesToShow.filter(line => !this.state.disabled[line]).map(label => {
      const boxID = label.split(' ')[1];
      const stat = label.split(' ')[2] === 'avg' ? 'average' : label.split(' ')[2];
      const data = trendData.filter(doc => doc.box_id === boxID).map(doc => [doc.timestamp_ms, doc[measurement][stat]]);
      return { label, data };
    });
  };

  generateReference = measurement => {
    let references;
    // @formatter:off
    switch (measurement) {
      case 'voltage': references = [114, 120, 126]; break;
      case 'frequency': references = [57, 60, 63]; break;
      case 'thd': references = [null, 0, 0.05]; break;
      default: break;
    }
    // @formatter:on
    return references;
  };

  legendClicked = label => {
    const disabled = this.state.disabled;
    disabled[label] = !disabled[label];
    this.setState({ disabled });
  };
}


LiveTrendDataManager.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array,
  measurement: PropTypes.string,
  timestamp: PropTypes.number,
  length: PropTypes.string,
  trendData: PropTypes.array,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ boxIDs, timestamp, length }) => {
  const start = Moment().subtract(1, length).valueOf();
  const end = Moment().valueOf();
  const timeRange = new TimeRange([start, end]);

  const sub = Meteor.subscribe('trends_after_timestamp', { timestamp, boxIDs });
  const trendData = Trends.find({
    timestamp_ms: { $gte: start },
    box_id: { $in: boxIDs }
  }, { sort: { timestamp_ms: 1 } }).fetch();

  return {
    ready: sub.ready(),
    trendData,
    start,
    end,
    timeRange,
  };
})(LiveTrendDataManager);
