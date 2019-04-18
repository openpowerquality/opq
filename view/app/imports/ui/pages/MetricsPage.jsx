import React from 'react';
import {Grid} from 'semantic-ui-react';

import MetricsInspector from "../components/MetricsInspector/MetricsInspector";

const MetricsPage = () => (
    <Grid container stackable>
        <Grid.Column width={16}>
            <MetricsInspector
                startTimestampS={1555113600}
                endTimestampS={1555117200}
            />
        </Grid.Column>
    </Grid>
);

export default MetricsPage;
