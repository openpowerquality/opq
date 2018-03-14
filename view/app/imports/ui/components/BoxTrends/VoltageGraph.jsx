import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Grid, Loader, Checkbox } from 'semantic-ui-react';

import { Trends } from '/imports/api/trends/TrendsCollection.js';

class VoltageGraph extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      showMax: false,
      showAverage: true,
      showMin: false,
    };

    this.updateGraph = this.updateGraph.bind(this);
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    const boxes = this.props.boxesToDisplay ? this.props.boxesToDisplay.map(boxID => `box${boxID}`) : ['1'];
    console.log(this.props.trends);
    const voltages = this.props.trends.map((trend) => ({
      [`box${trend.box_id}_timestamp_ms`]: trend.timestamp_ms,
      [`box${trend.box_id}_max`]: trend.voltage.max.toFixed(2),
      [`box${trend.box_id}_average`]: trend.voltage.average.toFixed(2),
      [`box${trend.box_id}_min`]: trend.voltage.min.toFixed(2),
    }));

    // Get the max and min values for the graph's Y axis
    let voltageUpperLimit = Math.max(...boxes.map(box =>
      Math.max(...voltages.map(voltage => (voltage[`${box}_max`] ? voltage[`${box}_max`] :
        Number.MIN_VALUE)))));
    let voltageLowerLimit = Math.min(...boxes.map(box =>
      Math.min(...voltages.map(voltage => (voltage[`${box}_min`] ? voltage[`${box}_min`] :
        Number.MAX_VALUE)))));

    // Reset them to something normal if we're not displaying any boxes
    voltageUpperLimit = this.props.boxesToDisplay ? voltageUpperLimit : 125;
    voltageLowerLimit = this.props.boxesToDisplay ? voltageLowerLimit : 115;

    return (
      <Grid container>
        <Grid.Row centered >
          <Grid.Column width={2} />
          <Grid.Column width={4} >
            <Checkbox toggle label='Max' onChange={this.updateGraph} checked={this.state.showMax}/>
          </Grid.Column>
          <Grid.Column width={5} >
            <Checkbox toggle label='Average' onChange={this.updateGraph} checked={this.state.showAverage}/>
          </Grid.Column>
          <Grid.Column width={5} >
            <Checkbox toggle label='Min' onChange={this.updateGraph} checked={this.state.showMin}/>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <ResponsiveContainer width='100%' aspect={2 / 1}>
            <AreaChart data={voltages}>
              <XAxis/>
              <YAxis domain={[voltageLowerLimit, voltageUpperLimit]}
                     label={{ value: 'Voltage', angle: -90 }}/>
              <Tooltip/>
              <CartesianGrid/>
              {boxes.map(box => (
                this.state.showMax ? <Area key={`${box}_max`} dataKey={`${box}_max`} connectNulls
                                           opacity={0.5} /> : ''
                // this.state.showAverage ? <Area key={`${box}_Average`} dataKey={`${box}_Average`} opacity={0.5}/> : '',
                // this.state.showMax ? <Area key={`${box}_min`} dataKey={`${box}_min`} opacity={0.5}/> : '',
              ))}
            </AreaChart>
          </ResponsiveContainer>
        </Grid.Row>
      </Grid>
    );
  }

  updateGraph() {
    return '';
  }

  generateMaxes(boxID, keyName) {
    const voltages = this.props.trends.map((trend) => ({
      timestamp_ms: trend.timestamp_ms,
      max: trend.voltage.max.toFixed(2), // Rounding for display purposes
      min: trend.voltage.min.toFixed(2),
      average: trend.voltage.average.toFixed(2),
    }));
    // Math.max and min don't take arrays; they take trailing args
    const voltageUpperLimit = Math.max(...voltages.map(voltage => voltage.max));
    const voltageLowerLimit = Math.min(...voltages.map(voltage => voltage.min));
  }
}

VoltageGraph.propTypes = {
  ready: PropTypes.bool.isRequired,
  trends: PropTypes.array,
  boxesToDisplay: PropTypes.array,
};

export default withTracker(() => {
  const trendsSub = Meteor.subscribe('get_recent_trends', { numTrends: 100 });
  const trends = Trends.find().fetch();
  return {
    ready: trendsSub.ready(),
    trends,
  };
})(VoltageGraph);
