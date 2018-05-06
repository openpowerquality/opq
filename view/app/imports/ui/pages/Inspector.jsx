import React from 'react';
import { Grid } from 'semantic-ui-react';

import EventInspector from '../components/EventInspector';

const Inspector = () => (
  <Grid container stackable>
    <Grid.Column width={16}>
      <EventInspector />
    </Grid.Column>
  </Grid>
);

export default Inspector;
