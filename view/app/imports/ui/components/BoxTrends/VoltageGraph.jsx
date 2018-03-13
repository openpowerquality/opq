import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Container, Loader, Checkbox } from 'semantic-ui-react';

import { Trends } from '/imports/api/trends/TrendsCollection.js';

class VoltageGraph extends React.Component {
  constructor(props) {
    super(props);

    this.setState({
      showMax: false,
      showAverage: true,
      showMin: false,
    });

    this.updateGraph = this.updateGraph.bind(this);
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    const boxesToDisplay = this.props.boxesToDisplay;
    const voltages = this.props.trends.map((trend) => ({
      [`${trend.box_id}timestamp_ms`]: trend.timestamp_ms,
      [`${trend.box_id}max`]: trend.voltage.max.toFixed(2),
      [`${trend.box_id}average`]: trend.voltage.average.toFixed(2),
      [`${trend.box_id}min`]: trend.voltage.min.toFixed(2),
    }));

    const voltageUpperLimit = Math.max(...boxesToDisplay.map(box_id =>
      Math.max(...voltages.map(voltage => voltage[`${box_id}max`]))));
    const voltageLowerLimit = Math.min(...boxesToDisplay.map(box_id =>
      Math.min(...voltages.map(voltage => voltage[`${box_id}min`]))));

    return (
      <Container>
        <Checkbox toggle label='Max' onChange={this.updateGraph} checked={this.state.showMax} />
        <Checkbox toggle label='Average' onChange={this.updateGraph} checked={this.state.showAverage} />
        <Checkbox toggle label='Min' onChange={this.updateGraph} checked={this.state.showMin} />
        <ResponsiveContainer width='100%' aspect={2 / 1}>
          <AreaChart data={voltages}>
            <XAxis />
            <YAxis domain={[voltageLowerLimit, voltageUpperLimit]}
                   label={{ value: 'Voltage', angle: -90 }} />
            <Tooltip />
            <CartesianGrid />
            {}

            <Area type='monotone' dataKey='max' opacity={0.5} />
            <Area type='monotone' dataKey='average' opacity={0.5} />
            <Area type='monotone' dataKey='min' opacity={0.5} />
          </AreaChart>
        </ResponsiveContainer>
      </Container>
    );
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
