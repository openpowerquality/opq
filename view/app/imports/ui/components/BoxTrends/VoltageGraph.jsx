import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, Label } from 'recharts';
import { Header, Grid, Loader, Checkbox, Container } from 'semantic-ui-react';

import { Trends } from '/imports/api/trends/TrendsCollection.js';

/*
 * !!!! THIS FILE IS CURRENTLY NOT BEING USED !!!!
 * It is being kept for reference purposes
 */


class VoltageGraph extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      boxIDs: ['1'],
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
    const boxIDs = this.props.boxesToDisplay;
    const voltages = {};
    boxIDs.forEach(boxID => {
      voltages[boxID] = {};
      voltages[boxID].data = this.props.trends.filter(trend => {
        return trend.box_id === boxID;
      }).map(trend => ({
        max: trend.voltage.max.toFixed(2),
        average: trend.voltage.average.toFixed(2),
        min: trend.voltage.min.toFixed(2),
        timestamp_ms: trend.timestamp_ms,
      }));
    });

    // Get the max and min values for the graph's X axis

    // Get the max and min values for the graph's Y axis
    boxIDs.forEach(boxID => {
      voltages[boxID].highest = Math.max(...voltages[boxID].data.map(voltage => voltage.max));
      voltages[boxID].lowest = Math.min(...voltages[boxID].data.map(voltage => voltage.min));
    });

    return (
      <Container>
      {boxIDs.map(boxID => (
      <Grid key={`box${boxID}`}>
        <Grid.Row centered>
          <Grid.Column width={3}>
            <Header as='h4' content={`Box ${boxID}`} textAlign='center'/>
          </Grid.Column>
          <Grid.Column width={4}>
            <Checkbox toggle label='Max' onChange={this.updateGraph} checked={this.state.showMax}/>
          </Grid.Column>
          <Grid.Column width={4}>
            <Checkbox toggle label='Min' onChange={this.updateGraph} checked={this.state.showMin}/>
          </Grid.Column>
          <Grid.Column width={5}>
            <Checkbox toggle label='Average' onChange={this.updateGraph} checked={this.state.showAverage}/>
          </Grid.Column>
        </Grid.Row>
          <Grid.Row>
            <ResponsiveContainer width='100%' aspect={2 / 1}>
              <AreaChart data={voltages[boxID].data}>
                <XAxis/>
                <YAxis domain={[voltages[boxID].lowest, voltages[boxID].highest]}/>
                <Tooltip/>
                <CartesianGrid/>
                {this.state.showMax ? <Area key={`box${boxID}_max`} dataKey='max' opacity={0.5}/> : ''}
                {this.state.showMin ? <Area key={`box${boxID}_min`} dataKey='min' opacity={0.5}/> : ''}
                {this.state.showAverage ? <Area key={`box${boxID}_average`} dataKey='average' opacity={0.5}/> : ''}
              </AreaChart>
            </ResponsiveContainer>
          </Grid.Row>

      </Grid>
      ))}
      </Container>
    );
  }

  updateGraph(event, data) {
    switch (data.label) {
      case 'Max': this.setState({ showMax: !this.state.showMax }); break;
      case 'Average': this.setState({ showAverage: !this.state.showAverage }); break;
      case 'Min': this.setState({ showMin: !this.state.showMin }); break;
      default: break;
    }
  }
}

VoltageGraph.propTypes = {
  ready: PropTypes.bool.isRequired,
  trends: PropTypes.array,
  boxesToDisplay: PropTypes.array,
};

export default withTracker(() => {
  const trendsSub = Meteor.subscribe('get_recent_trends', { numTrends: 120 });
  const trends = Trends.find().fetch();
  return {
    ready: trendsSub.ready(),
    trends,
  };
})(VoltageGraph);
