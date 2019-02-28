import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxTrends from '../components/BoxTrends';
import SystemStats from '../components/SystemStats';
import SystemHealth from '../components/SystemHealth';

const Landing = () => (
  <Grid container stackable>
    <Grid.Row stretched>
      <Grid.Column width={6}>
        <SystemStats/>
        <SystemHealth/>
      </Grid.Column>
      <Grid.Column width={10}>
        <BoxTrends/>
      </Grid.Column>
    </Grid.Row>
  </Grid>
);

export default Landing;
