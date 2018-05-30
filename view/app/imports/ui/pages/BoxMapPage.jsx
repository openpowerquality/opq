import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxMap from '../components/BoxMap/BoxMap';
import WidgetPanel from '../layouts/WidgetPanel';

const BoxMapPage = () => (
    <Grid container stackable>
      <Grid.Column width={16}>
        <WidgetPanel title="Box Map" noPadding={true}>
          <BoxMap/>
        </WidgetPanel>
      </Grid.Column>
    </Grid>
);

export default BoxMapPage;
