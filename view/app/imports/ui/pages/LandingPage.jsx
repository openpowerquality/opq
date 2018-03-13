import React from 'react';
import { Grid, Segment } from 'semantic-ui-react';

import BoxTrends from '../components/BoxTrends/BoxTrends.jsx';

class LandingPage extends React.Component {
  render() {
    return (
      <Grid container stackable>
        <Grid.Row stretched>
          <Grid.Column width={5}>
            <Segment>
              <h3>SystemStats</h3>
            </Segment>
            <Segment>
              <h3>SystemHealth</h3>
            </Segment>
          </Grid.Column>
          <Grid.Column width={11}>
            <Segment>
              <h3>BoxMap</h3>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row stretched>
          <Grid.Column width={5}>
            <Segment>
              <h3>LiveBoxMonitor</h3>
            </Segment>
          </Grid.Column>
          <Grid.Column width={11} stretched>
            <BoxTrends />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Segment>
              <h3>EventsTimeline</h3>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Segment>
              <h3>EventDetail</h3>
            </Segment>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    );
  }
}

export default LandingPage;
