import React from 'react';
import { Grid } from 'semantic-ui-react';

import IncidentInspector from '../components/IncidentInspector/IncidentInspector';

const IncidentInspectorPage = () => (
    <Grid container stackable>
        <Grid.Column width={16}>
            <IncidentInspector />
        </Grid.Column>
    </Grid>
);

export default IncidentInspectorPage;
