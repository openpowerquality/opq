import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxMap from '../components/BoxMap';
import WidgetPanel from '../layouts/WidgetPanel';

const BoxMapPage = () => (
    <Grid container stackable>
      <Grid.Column width={16}>
        <WidgetPanel title="Box Map">
          <BoxMap/>
        </WidgetPanel>
      </Grid.Column>
    </Grid>
);

export default BoxMapPage;
