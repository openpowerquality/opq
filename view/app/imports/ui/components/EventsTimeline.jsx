import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Loader } from 'semantic-ui-react';
import { Events } from '/imports/api/events/EventsCollection';
import { Charts, ChartContainer, ChartRow, YAxis, BarChart, Resizable, styler, Legend } from 'react-timeseries-charts';
import { TimeSeries, sum } from 'pondjs';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';
import colors from '../utils/colors';

/* eslint max-len: 0 */

/** Display Events */
class EventsTimeline extends React.Component {

  constructor(props) {
    super(props);
    this.renderPage = this.renderPage.bind(this);
    this.state = { timerange: null };
  }

  helpText = `
  <p>Events Timeline shows a visual summary of the numbers and types of events noticed by OPQ Boxes.</p>
  
  <p>See the legend to determine the types of events noticed. </p>
  
  <p>This visualization supports panning and zooming.  Scroll the mouse up or down over the visualization to change
  the time interval. Click and drag right or left to change the window of time displayed.</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  renderPage() { // eslint-disable-line class-methods-use-this

    const numEvents = this.props.events.length;
    // Start with the list of event types:
    const eventTypes = Events.eventTypes;
    // Create a list of lists, each sublist is a list of Events of the corresponding event type.
    const eventsList = eventTypes.map(eventType => this.props.events.filter(event => event.type === eventType));
    const eventTypeCounts = eventsList.map(events => events.length);
    // Convert the sublists into pairs of timestamps and 1, so we can create TimeSeries.
    const eventsPairsList = eventsList.map(events => events.map(event => [event.target_event_start_timestamp_ms, 1]));
    // Create a single TimeSeries object per Event Type. The Event Type name is both the TimeSeries name and the column name.
    const timeSeriesList = eventsPairsList.map((eventsPairs, index) => new TimeSeries({ name: eventTypes[index], columns: ['time', eventTypes[index]], points: eventsPairs }));
    // Merge all the individual TimeSeries lists into a single one with columns for each event type.
    const rawSeries = TimeSeries.timeSeriesListMerge({ name: 'event-types', seriesList: timeSeriesList });

    // This is a little complicated. We need the aggregation object to look like:
    // { FREQUENCY_SAG: { FREQUENCY_SAG: sum() }, FREQUENCY_SWELL: { FREQUENCY_SWELL: sum() }, .... }
    // Seems easiest to just construct it by hand. This will break if we ever change the number of Event Types!!!!
    const aggregation = {
      [eventTypes[0]]: { [eventTypes[0]]: sum() },
      [eventTypes[1]]: { [eventTypes[1]]: sum() },
      [eventTypes[2]]: { [eventTypes[2]]: sum() },
      [eventTypes[3]]: { [eventTypes[3]]: sum() },
      [eventTypes[4]]: { [eventTypes[4]]: sum() },
      [eventTypes[5]]: { [eventTypes[5]]: sum() },
    };

    // Create a "rollup" which produces Indexed time intervals with the number of events in them at an hourly basis.
    const series = rawSeries.fixedWindowRollup({ windowSize: '6h', aggregation });
    // Should calculate this via reduce. Need to see if TimeSeries has a convenience function for this.
    // There appears to be no simple way to compute this other than to find the max of all the rows by hand.
    // That's ridiculous. So, I'm going to heuristically approximate it.
    const maxYAxis = 0.75 * (series.max(eventTypes[0]) + series.max(eventTypes[1]) + series.max(eventTypes[2]) +
      series.max(eventTypes[3]) + series.max(eventTypes[4]) + series.max(eventTypes[5]));

    // Create the styler so we can distinguish between the various event types.
    const stylerArg = eventTypes.map((eventType, index) => ({ key: eventType, color: colors[index], selected: 'red' }));
    const style = styler(stylerArg);

    // Create the Legend categories so we know which event types the colors refer to.
    const legendCategories = eventTypes.map((eventType, index) => ({ key: eventType, label: `${eventType} (${eventTypeCounts[index]})` }));

    const divStyle = { paddingLeft: '20px', paddingRight: '20px' };
    const title = `Events Timeline (most recent ${numEvents} events)`;
    return (
        <WidgetPanel title={title} helpText={this.helpText}>
          <div style={divStyle}>
            <Resizable>
              <ChartContainer
                  enablePanZoom={true}
                  timeRange={this.state.timerange || series.range() }
                  onTimeRangeChanged={timerange => this.setState({ timerange })}>
                <ChartRow height='150'>
                  <YAxis id='num-events' label='Num Events' min={0} max={maxYAxis} width='70' type='linear'/>
                  <Charts>
                    <BarChart axis='num-events' style={style} spacing={1} columns={eventTypes} series={series}
                              minBarHeight={1} />
                  </Charts>
                </ChartRow>
              </ChartContainer>
            </Resizable>
            <Legend categories={legendCategories} style={style} type='swatch' />
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
  const sub = Meteor.subscribe(Events.publicationNames.GET_RECENT_EVENTS, { numEvents: 500, excludeOther: false });
  return {
    ready: sub.ready(),
    events: Events.find({}, { sort: { target_event_start_timestamp_ms: 1 } }).fetch(),
  };
})(EventsTimeline);

