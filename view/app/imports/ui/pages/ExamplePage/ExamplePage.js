import React from 'react';
import ExampleTable from '../../components/ExampleTable/ExampleTable';
import {Grid} from 'semantic-ui-react'

const ExamplePage = () => (
  <Grid centered verticalAlign='middle' columns={3}>
    <Grid.Row></Grid.Row>
    <Grid.Row>
      <Grid.Column></Grid.Column>
      <Grid.Column>
        <ExampleTable/>
      </Grid.Column>
      <Grid.Column></Grid.Column>
    </Grid.Row>
  </Grid>
)

export default ExamplePage
