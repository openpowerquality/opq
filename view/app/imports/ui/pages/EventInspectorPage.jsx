import React from 'react';
import { Grid } from 'semantic-ui-react';

import EventInspector from '../components/EventInspector/EventInspector';

const EventInspectorPage = () => (
  <Grid container stackable>
    <Grid.Column width={16}>
      <EventInspector />
    </Grid.Column>
  </Grid>
);

export default EventInspectorPage;
