import React from 'react';
import {Container, Grid} from 'semantic-ui-react';

import { LahaStats } from '../../api/laha-stats/LahaStatsCollection';
import { getLahaStatsInRange } from '../../api/laha-stats/LahaStatsCollection.methods';
import MetricsInspector from "../components/MetricsInspector/MetricsInspector";

getLahaStatsInRange.call(
    {startTimestampS: 0,
           endTimestampS: 999999999999999999},
    (error, lahaStats) => {
    console.log(error, lahaStats);
    });

const MetricsPage = () => (
    <Grid container stackable>
        <Grid.Column width={16}>
            <MetricsInspector />
        </Grid.Column>
    </Grid>
);

export default MetricsPage;
