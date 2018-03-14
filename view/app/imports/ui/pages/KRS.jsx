import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Container, Header, Grid, Loader, Segment } from 'semantic-ui-react';
import {
  ResponsiveContainer, AreaChart, Area, LineChart, Line, XAxis, YAxis,
  Legend, Tooltip, CartesianGrid
} from 'recharts';

import { Trends } from '../../api/trends/TrendsCollection.js';
import { monthlyBoxTrends } from '../../api/trends/TrendsCollectionMethods';
const data = [
  {name: 'Page A', uv: 4000},
  {name: 'Page B', uv: 3000},
  {name: 'Page C', uv: 2000},
  {name: 'Page D'},
  {name: 'Page E', uv: 1890},
  {name: 'Page F', uv: 2390},
  {name: 'Page G', uv: 3490},
];
class KRS extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dailyTrends: null,
    };
  }
  dailyTrends(box_id, month, year) {
    let data = [];
    monthlyBoxTrends.call({ box_id: box_id, month: month, year: year }, (error, { dailyTrends }) => {
      if (error) {
        console.log(error);
      } else {
        data = _.values(dailyTrends);
      }
    });
    return data;
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active size={'massive'}>Loading...</Loader>;
  }

  renderPage() {
    const voltages = this.props.trends.map((trend) => ({
      timestamp: trend.timestamp_ms,
      voltageMax: trend.voltage.max,
      voltageMin: trend.voltage.min,
      voltageAverage: trend.voltage.average,
    }));

    return (
      <Container>
        <div>
          <AreaChart width={600} height={200} data={data}
                     margin={{top: 10, right: 30, left: 0, bottom: 0}}>
            <XAxis dataKey="name"/>
            <YAxis/>
            <CartesianGrid strokeDasharray="3 3"/>
            <Tooltip/>
            <Area type='monotone' dataKey='uv' stroke='#8884d8' fill='#8884d8' />
          </AreaChart>
          <AreaChart width={600} height={200} data={data}
                     margin={{top: 10, right: 30, left: 0, bottom: 0}}>
            <XAxis dataKey="name"/>
            <YAxis/>
            <CartesianGrid strokeDasharray="3 3"/>
            <Tooltip/>
            <Area connectNulls={true} type='monotone' dataKey='uv' stroke='#8884d8' fill='#8884d8' />
          </AreaChart>
        </div>
        <Header as={'h1'} textAlign='center'>Recharts trends</Header>
        <Grid centered>
          <Grid.Row>
            <Grid.Column width={8} textAlign={'center'}>
              <Header as={'h2'}>LineChart</Header>
              <Segment>
              <ResponsiveContainer width='100%' aspect={5 / 3}>
                <LineChart data={voltages}>
                  <XAxis/>
                  <YAxis domain={[115, 125]}/>
                  <Legend/>
                  <Tooltip/>
                  <Line type="monotone" dataKey="voltageMax" stroke="#8884d8"/>
                  <Line type="monotone" dataKey="voltageMin" stroke="#563633"/>
                  <Line type="monotone" dataKey="voltageAverage" stroke="#d67536"/>
                </LineChart>
              </ResponsiveContainer>
              </Segment>
            </Grid.Column>
            <Grid.Column width={8} textAlign={'center'}>
              <Header as={'h2'}>AreaChart</Header>
              <ResponsiveContainer width='100%' aspect={5 / 3}>
                <AreaChart data={voltages}>
                  <XAxis dataKey={'timestamp'}/>
                  <YAxis domain={[115, 125]}/>
                  <Legend/>
                  <Tooltip/>
                  <Area type="monotone" dataKey="voltageMax" stroke="#99EAFF"/>
                  <Area type="monotone" dataKey="voltageMin" stroke="#563633"/>
                  <Area type="monotone" dataKey="voltageAverage" stroke="#d67536"/>
                </AreaChart>
              </ResponsiveContainer>
            </Grid.Column>
          </Grid.Row>
          <Grid.Row>
            <Grid.Column textAlign={'center'}>
              <Header as={'h2'}>Box 4 uptime during January</Header>
              <ResponsiveContainer width={'100%'} aspect={3}>
                <AreaChart data={this.dailyTrends(4, 1, 2018)}>
                  <XAxis/>
                  <YAxis/>
                  <CartesianGrid/>
                  <Legend/>
                  <Tooltip/>
                  <Area type="monotone" dataKey="uptime" stroke="#99EAFF" fill='#99EAFF'/>
                </AreaChart>
              </ResponsiveContainer>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Container>
    );
  }
}

KRS.propTypes = {
  trends: PropTypes.array,
  ready: PropTypes.bool,
};

export default withTracker(() => {
  const trendsHandle = Meteor.subscribe('get_recent_trends', { numTrends: 20 });
  const trends = Trends.find().fetch();

  return {
    trends,
    ready: trendsHandle.ready(),
  };
})(KRS);
