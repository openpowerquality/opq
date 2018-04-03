import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Loader } from 'semantic-ui-react';
import { Events } from '/imports/api/events/EventsCollection';
import { Charts, ChartContainer, ChartRow, YAxis, BarChart, Resizable, styler } from 'react-timeseries-charts';
import { TimeSeries, sum } from 'pondjs';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display Events */
class EventsTimeline extends React.Component {

  constructor(props) {
    super(props);
    this.renderPage = this.renderPage.bind(this);
    this.timerange = null;
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  renderPage() { // eslint-disable-line class-methods-use-this
    const data = this.props.events.map(event => [event.target_event_start_timestamp_ms, 1]);

    const rawSeries = new TimeSeries({
      name: 'Recent Events',
      columns: ['time', 'value'],
      points: data,
    });

    const series = rawSeries.fixedWindowRollup({ windowSize: '12h', aggregation: { value: { value: sum() } } });
    const style = styler([{ key: 'value', color: 'skyblue', selected: 'brown' }]);
    if (this.state.timerange === null) {
      this.setState({ timerange: series.range() });
    }

    const divStyle = { paddingLeft: '20px', paddingRight: '20px' };
    return (
        <WidgetPanel title='Recent Events'>
          <div style={divStyle}>
            <Resizable>
              <ChartContainer
                  enablePanZoom={true}
                  timeRange={this.state.timerange}
                  onTimeRangeChanged={timerange => this.setState({ timerange })}>
                <ChartRow height='150'>
                  <YAxis
                      id='num-events'
                      label='Num Events'
                      min={0}
                      max={series.max('value')}

                      width='70'
                      type='linear'
                  />
                  <Charts>
                    <BarChart
                        axis='num-events'
                        style={style}
                        spacing={1}
                        columns={['value']}
                        series={series}
                        minBarHeight={1}
                    />
                  </Charts>
                </ChartRow>
              </ChartContainer>
            </Resizable>
          </div>
        </WidgetPanel>
    );
  }

}

/** Require an array of Stuff documents in the props. */
EventsTimeline.propTypes = {
  ready: PropTypes.bool.isRequired,
  events: PropTypes.array.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const eventsSub = Meteor.subscribe(Events.publicationNames.GET_RECENT_EVENTS, { numEvents: 500, excludeOther: true });
  return {
    ready: eventsSub.ready(),
    events: Events.find({}).fetch(),
  };
})(EventsTimeline);

