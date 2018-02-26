import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Container, Header, Grid, Loader, Message } from 'semantic-ui-react';
import {
  ResponsiveContainer, AreaChart, Area, LineChart, Line, XAxis, YAxis,
  Legend, Tooltip, CartesianGrid
} from 'recharts';
import SimpleSchema from 'simpl-schema';

import { Trends } from '../../api/trends/TrendsCollection.js';
import { monthlyBoxTrends } from '../../api/trends/TrendsCollectionMethods';
import LoginForm from '../components/LoginForm';

const schema = new SimpleSchema({
  email: {
    type: String,
  },
  password: {
    type: String,
  },
});


class KRS extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      dailyTrends: null,
      email: '',
      password: '',
      error: '',
    };

    this.update = this.update.bind(this);
    this.login = this.login.bind(this);
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
  update(key, value) {
    console.log({ key, value });
    this.setState({ [key]: value });
  }
  login(mod) {
    const email = mod.email;
    const password = mod.password;

    Meteor.loginWithPassword(email, password, (err) => {
      if (err) {
        this.setState({
          error: err.reason, // {error} will be rendered below
        });
      } else {
        this.setState({
          error: '',
        });
      }
    });
  }
  render() {
    return this.props.ready ? this.renderPage() :
      <Loader active size={'massive'}>Loading...</Loader>;
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
        <LoginForm schema={schema} onSubmit={this.login}/>
        <Message
          error
          content={this.state.error}
        />
        <Header as={'h1'} textAlign='center'>Recharts trends</Header>
        <Grid centered>
          <Grid.Row>
            <Grid.Column width={8} textAlign={'center'}>
              <Header as={'h2'}>LineChart</Header>
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
  const trends = Trends.find()
    .fetch();

  return {
    trends,
    ready: trendsHandle.ready(),
  };
})(KRS);
