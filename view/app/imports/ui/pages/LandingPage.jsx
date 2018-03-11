import React from 'react';
import { Grid, Segment } from 'semantic-ui-react';

class LandingPage extends React.Component {
  render() {
    return (
      <Grid container stackable textAlign="center" >
        <Grid.Row stretched>
          <Grid.Column width={5}>
            <Segment>
              <h1>SystemStats</h1>
            </Segment>
            <Segment>
              <h1>SystemHealth</h1>
            </Segment>
          </Grid.Column>
          <Grid.Column width={11}>
            <Segment>
              <h1>BoxMap</h1>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row stretched>
          <Grid.Column width={5}>
            <Segment>
              <h1>LiveBoxMonitor</h1>
            </Segment>
          </Grid.Column>
          <Grid.Column width={11}>
            <Segment>
              <h1>BoxTrends</h1>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Segment>
              <h1>EventsTimeline</h1>
            </Segment>
          </Grid.Column>
        </Grid.Row>
        <Grid.Row>
          <Grid.Column>
            <Segment>
              <h1>EventDetail</h1>
            </Segment>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    );
  }
}

export default LandingPage;
