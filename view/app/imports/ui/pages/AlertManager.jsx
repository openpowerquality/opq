import React from 'react';
import { Grid } from 'semantic-ui-react';

import AlertSpec from '../components/Alerts/AlertSpec';
import AlertITIC from '../components/Alerts/AlertITIC';

const AlertManager = () => (
    <Grid container stackable>
      <Grid.Column width={16}>
        <AlertSpec />
        <AlertITIC />
      </Grid.Column>
    </Grid>
);

export default AlertManager;
