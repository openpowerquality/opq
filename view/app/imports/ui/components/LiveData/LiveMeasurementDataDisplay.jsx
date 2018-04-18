import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Header, Container, Grid } from 'semantic-ui-react';
import Moment from 'moment';
import {
  Charts, ChartContainer, ChartRow, YAxis, LineChart, Baseline, Resizable, Legend, styler,
} from 'react-timeseries-charts';
import { TimeRange, TimeSeries } from 'pondjs';

import { Measurements } from '../../../api/measurements/MeasurementsCollection';

import colors from '../../utils/colors';

class LiveMeasurementDataManager extends React.Component {
  render() {
    return this.props.ready ? this.renderPage() : '';
  }

  renderPage = () => {
    return (
      this.generateGraph(this.props.measurement)
    );
  };


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

    const graphData = this.getGraphData(measurement);
    const reference = this.generateReference(measurement);
    const wholeDataSet = [];
    graphData.data.forEach(point => { wholeDataSet.push(point[1]); });
    reference.forEach(value => { wholeDataSet.push(value); });

    return (
      <div>
        <Header as='h3' content={headerContent}/>
        <Resizable>
          <ChartContainer timeRange={this.props.timeRange}>
            <ChartRow height='300'>
              <YAxis id={measurement} format={n => n.toFixed(2)}
                     min={Math.min(...wholeDataSet)} max={Math.max(...wholeDataSet)}/>
              <Charts>
                <LineChart key={graphData.label} axis={measurement} series={new TimeSeries({
                  name: graphData.label,
                  columns: ['time', 'value'],
                  points: graphData.data,
                })} style={{ value: { normal: { strokeWidth: 2 } } }}/>
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

  getGraphData = (measurement) => {
    const measurementData = this.props.measurementData;
    const boxID = this.props.boxID;
    const data = measurementData.filter(doc => doc.box_id === boxID).map(doc => [doc.timestamp_ms, doc[measurement]]);
    return { label: boxID, data };
  };

  generateReference = (measurement) => {
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
}


LiveMeasurementDataManager.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxID: PropTypes.string,
  measurement: PropTypes.string,
  measurementData: PropTypes.array,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ boxID }) => {
  const start = Moment().subtract(30, 'seconds').valueOf();
  const end = Moment().valueOf();
  const timeRange = new TimeRange([start, end]);

  const sub = Meteor.subscribe('recent_measurements', 30, boxID);
  const measurementData = Measurements.find({
    timestamp_ms: { $gte: start },
    box_id: boxID,
  }, { sort: { timestamp_ms: 1 } }).fetch();

  return {
    ready: sub.ready(),
    measurementData,
    start,
    end,
    timeRange,
  };
})(LiveMeasurementDataManager);
