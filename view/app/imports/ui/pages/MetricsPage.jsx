import React from 'react';
import {Grid} from 'semantic-ui-react';

import MetricsInspector from '../components/MetricsInspector/MetricsInspector';

const endTimestampS = Math.fround((new Date()).getTime() / 1000);
const startTimestampS = endTimestampS - 86400;

const MetricsPage = () => (
    <Grid container stackable>
        <Grid.Column width={16}>
            <MetricsInspector
                startTimestampS={startTimestampS}
                endTimestampS={endTimestampS}
            />
        </Grid.Column>
    </Grid>
);

export default MetricsPage;
