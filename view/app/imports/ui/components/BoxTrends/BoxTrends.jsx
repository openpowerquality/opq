import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Loader, Container, Segment, Header, Dropdown, Checkbox } from 'semantic-ui-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

import { getBoxIDs } from '/imports/api/opq-boxes/OpqBoxesCollectionMethods.js';
import { Trends } from '/imports/api/trends/TrendsCollection.js';

class BoxTrends extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      boxIdOptions: [],
      selectedBoxes: ['1'],
      graph: 'voltage',
      showMax: false,
      showMin: false,
      showAverage: true,
      trends: [],
    };

    getBoxIDs.call((error, boxIDs) => {
      if (error) {
        console.log(error);
      } else {
        this.setState({
          boxIdOptions: boxIDs.sort().map(ID => ({
            text: `Box ${ID}`,
            value: ID,
          })),
        });
      }
    });

    this.updateBoxIdDropdown = this.updateBoxIdDropdown.bind(this);
    this.changeGraph = this.changeGraph.bind(this);
    this.changeChecked = this.changeChecked.bind(this);
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    const graphData = {};
    this.state.selectedBoxes.forEach(boxID => {
      graphData[boxID] = {};
      graphData[boxID].data = this.props.trends.filter(trend => trend.box_id === boxID).map(trend => ({
        max: trend[this.state.graph].max.toFixed(2),
        average: trend[this.state.graph].average.toFixed(2),
        min: trend[this.state.graph].min.toFixed(2),
        timestamp_ms: trend.timestamp_ms,
      }));
    });

    // Get the max and min values for the graph's X axis

    // Get the max and min values for the graph's Y axis
    this.state.selectedBoxes.forEach(boxID => {
      graphData[boxID].highest = Math.max(...graphData[boxID].data.map(item => item.max));
      graphData[boxID].lowest = Math.min(...graphData[boxID].data.map(item => item.min));
    });

    return (
      <Container>
        <Segment attached='top'>
          <Header as='h3' icon='line chart' content='Trends' floated='left' />
          <Dropdown placeholder='Boxes to display' multiple search selection
                    options={this.state.boxIdOptions}
                    onChange={this.updateBoxIdDropdown}
                    defaultValue={this.state.selectedBoxes} />
          <Dropdown placeholder='Graph to display' search selection
                    options={[
                      { text: 'Voltage', value: 'voltage' },
                      { text: 'Frequency', value: 'frequency' },
                    ]}
                    onChange={this.changeGraph}
                    defaultValue={this.state.graph} />
        </Segment>
        <Segment attached='bottom'>
          {this.state.selectedBoxes.map(boxID => (
            <Grid key={`box${boxID}`}>
              <Grid.Row centered>
                <Grid.Column width={3}>
                  <Header as='h4' content={`Box ${boxID}`} textAlign='center'/>
                </Grid.Column>
                <Grid.Column width={4}>
                  <Checkbox toggle label='Max' onChange={this.changeChecked} checked={this.state.showMax}/>
                </Grid.Column>
                <Grid.Column width={4}>
                  <Checkbox toggle label='Min' onChange={this.changeChecked} checked={this.state.showMin}/>
                </Grid.Column>
                <Grid.Column width={5}>
                  <Checkbox toggle label='Average' onChange={this.changeChecked} checked={this.state.showAverage}/>
                </Grid.Column>
              </Grid.Row>
              <Grid.Row>
                <ResponsiveContainer width='100%' aspect={2 / 1}>
                  <AreaChart data={graphData[boxID].data}>
                    <XAxis/>
                    <YAxis domain={[graphData[boxID].lowest, graphData[boxID].highest]}/>
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
        </Segment>
      </Container>
    );
  }

  updateBoxIdDropdown(event, data) {
    this.setState({ selectedBoxes: data.value });
  }

  changeGraph(event, data) {
    this.setState({ graph: data.value });
  }

  changeChecked(event, data) {
    switch (data.label) {
      case 'Max': this.setState({ showMax: !this.state.showMax }); break;
      case 'Average': this.setState({ showAverage: !this.state.showAverage }); break;
      case 'Min': this.setState({ showMin: !this.state.showMin }); break;
      default: break;
    }
  }
}

BoxTrends.propTypes = {
  ready: PropTypes.bool.isRequired,
  trends: PropTypes.array,
};

export default withTracker(() => {
  const trendsSub = Meteor.subscribe('get_recent_trends', { numTrends: 120 });
  const trends = Trends.find().fetch();
  return {
    ready: trendsSub.ready(),
    trends,
  };
})(BoxTrends);
