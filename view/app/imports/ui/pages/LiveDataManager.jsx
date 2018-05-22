import React from 'react';
import { Grid } from 'semantic-ui-react';

import LiveTrendDataManager from '../components/LiveData/LiveTrendDataManager';
import LiveMeasurementDataManager from '../components/LiveData/LiveMeasurementDataManager';

const LiveDataManager = () => (
  <Grid container stackable>
    <Grid.Column width={16}>
      <LiveTrendDataManager />
    </Grid.Column>
    <Grid.Column width={16}>
      <LiveMeasurementDataManager/>
    </Grid.Column>
  </Grid>
);

export default LiveDataManager;
