import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxMap from '../components/BoxMap/BoxMap';

const BoxMapPage = () => (
    <Grid container stackable>
      <Grid.Column width={16}>
        <BoxMap/>
      </Grid.Column>
    </Grid>
);

export default BoxMapPage;
