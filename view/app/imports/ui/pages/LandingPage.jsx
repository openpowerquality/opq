import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxTrends from '../components/BoxTrends';
import SystemStats from '../components/SystemStats';
import SystemHealth from '../components/SystemHealth';
import LiveBoxMonitor from '../components/LiveBoxMonitor';
import BoxMap from '../components/BoxMap';
import EventsTimeline from '../components/EventsTimeline';
import EventDetail from '../components/EventDetail';

const LandingPage = () => (
  <Grid container stackable>
    <Grid.Row stretched>
      <Grid.Column width={5}>
        <SystemStats/>
        <SystemHealth/>
      </Grid.Column>
      <Grid.Column width={11}>
        <BoxMap/>
      </Grid.Column>
    </Grid.Row>

    <Grid.Row stretched>
      <Grid.Column width={5}>
        <LiveBoxMonitor/>
      </Grid.Column>
      <Grid.Column width={11} stretched>
        <BoxTrends />
      </Grid.Column>
    </Grid.Row>

    <Grid.Row>
      <Grid.Column>
        <EventsTimeline/>
      </Grid.Column>
    </Grid.Row>

    <Grid.Row>
      <Grid.Column>
        <EventDetail/>
      </Grid.Column>
    </Grid.Row>
  </Grid>
);

export default LandingPage;
