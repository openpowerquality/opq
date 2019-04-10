import React from 'react';
import { Container } from 'semantic-ui-react';

import { LahaStats } from '../../api/laha-stats/LahaStatsCollection';
import { getLahaStatsInRange } from '../../api/laha-stats/LahaStatsCollection.methods';

getLahaStatsInRange.call(
    {startTimestampS: 0,
           endTimestampS: 999999999999999999},
    (error, lahaStats) => {
    console.log(error, lahaStats);
    });

const Metrics = () => (
    <Container text>
      <p>This page will eventually contain metrics regarding OPQ Cloud.</p>
    </Container>
);

export default Metrics;
