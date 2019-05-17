import React from 'react';
import { Grid } from 'semantic-ui-react';

import MetricsInspector from '../components/MetricsInspector/MetricsInspector';

const MetricsPage = () => (
    <Grid container stackable>
        <Grid.Column width={16}>
            <MetricsInspector />
        </Grid.Column>
    </Grid>
);

export default MetricsPage;
