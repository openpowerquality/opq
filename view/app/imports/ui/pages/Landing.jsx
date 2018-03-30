import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxTrends from '../components/BoxTrends';
import SystemStats from '../components/SystemStats';
import SystemHealth from '../components/SystemHealth';
import LiveBoxMonitor from '../components/LiveBoxMonitor';

const Landing = () => (
  <Grid container stackable>
    <Grid.Row stretched>
      <Grid.Column width={5}>
        <SystemStats/>
        <SystemHealth/>
        <LiveBoxMonitor/>
      </Grid.Column>
      <Grid.Column width={11}>
        <BoxTrends/>
      </Grid.Column>
    </Grid.Row>
  </Grid>
);

export default Landing;
