import React from 'react';
import { Meteor } from 'meteor/meteor';
import Moment from 'moment';
import { Loader } from 'semantic-ui-react';
import { Events } from '/imports/api/events/EventsCollection';
import { Charts, ChartContainer, ChartRow, YAxis, BarChart, Resizable, styler } from 'react-timeseries-charts';
import { TimeSeries, Index, TimeRangeEvent, TimeRange, count } from 'pondjs';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display Events */
class EventsTimeline extends React.Component {

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage3() : <Loader>Getting data</Loader>;
  }

  renderPage() { // eslint-disable-line class-methods-use-this

    const eventList = this.props.events.map(event => [event.target_event_start_timestamp_ms, 1]);
    const timeStamps = this.props.events.map(event => Moment(event.target_event_start_timestamp_ms).format('lll'));
    console.log('eventList', eventList);
    console.log('timestamps', timeStamps);
    const rawSeries = new TimeSeries({ name: 'Events', columns: ['time', 'value'], points: eventList });
    console.log('rawSeries', rawSeries);
    const series = rawSeries.dailyRollup({ aggregation: { value: { value: count() } } });
    console.log('rollup series', series);
    console.log('series range', series.range());

    return (
        <WidgetPanel title='Events Timeline'>
          <Resizable>
            <ChartContainer timeRange={rawSeries.range()}>
              <ChartRow height='150'>
                <Charts>
                  <YAxis
                    id='rain'
                    label='Events'
                    min={0}
                    max={50}
                    width='70'
                    type='linear'
                  />
                  <BarChart
                    axis='rain'
                    spacing={1}
                    columns={['value']}
                    minBarHeight={1}
                    series={rawSeries}
                  />
                </Charts>
              </ChartRow>
            </ChartContainer>
          </Resizable>
        </WidgetPanel>
    );
  }

  renderPage3() { // eslint-disable-line class-methods-use-this

    const eventList = this.props.events.map(event => [event.target_event_start_timestamp_ms, 1]);
    const indexedEventList = eventList.map(event => [Index.getIndexString('1s', event[0]), 1]);
    const series = new TimeSeries({ name: 'Events', columns: ['index', 'value'], points: indexedEventList });

    return (
        <WidgetPanel title='Events Timeline'>
          <Resizable>
            <ChartContainer timeRange={series.range()}>
              <ChartRow height='150'>
                <YAxis
                    id='rain'
                    label='Rainfall (inches/hr)'
                    min={0}
                    max={1.5}
                    format='.2f'
                    width='70'
                    type='linear'
                />
                <Charts>
                  <BarChart
                      axis='rain'
                      spacing={1}
                      columns={['precip']}
                      series={series}
                      minBarHeight={1}
                  />
                </Charts>
              </ChartRow>
            </ChartContainer>
          </Resizable>
        </WidgetPanel>
    );
  }
  renderPage2() { // eslint-disable-line class-methods-use-this

    const data = [
      ['2017-01-24 00:00', 0.01],
      ['2017-01-24 01:00', 0.13],
      ['2017-01-24 02:00', 0.07],
      ['2017-01-24 03:00', 0.04],
      ['2017-01-24 04:00', 0.33],
      ['2017-01-24 05:00', 0],
      ['2017-01-24 06:00', 0],
      ['2017-01-24 07:00', 0],
      ['2017-01-24 08:00', 0.95],
      ['2017-01-24 09:00', 1.12],
      ['2017-01-24 10:00', 0.66],
      ['2017-01-24 11:00', 0.06],
      ['2017-01-24 12:00', 0.3],
      ['2017-01-24 13:00', 0.05],
      ['2017-01-24 14:00', 0.5],
      ['2017-01-24 15:00', 0.24],
      ['2017-01-24 16:00', 0.02],
      ['2017-01-24 17:00', 0.98],
      ['2017-01-24 18:00', 0.46],
      ['2017-01-24 19:00', 0.8],
      ['2017-01-24 20:00', 0.39],
      ['2017-01-24 21:00', 0.4],
      ['2017-01-24 22:00', 0.39],
      ['2017-01-24 23:00', 0.28],
    ];

    const series = new TimeSeries({
      name: 'hilo_rainfall',
      columns: ['index', 'precip'],
      points: data.map(([d, value]) => [Index.getIndexString('1h', new Date(d)), value]),
    });

    return (
        <WidgetPanel title='Events Timeline'>
          <Resizable>
            <ChartContainer timeRange={series.range()}>
              <ChartRow height='150'>
                <YAxis
                    id='rain'
                    label='Rainfall (inches/hr)'
                    min={0}
                    max={1.5}
                    format='.2f'
                    width='70'
                    type='linear'
                />
                <Charts>
                  <BarChart
                      axis='rain'
                      spacing={1}
                      columns={['precip']}
                      series={series}
                      minBarHeight={1}
                  />
                </Charts>
              </ChartRow>
            </ChartContainer>
          </Resizable>
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
  const eventsSub = Meteor.subscribe(Events.publicationNames.GET_RECENT_EVENTS, { numEvents: 50, excludeOther: true });
  return {
    ready: eventsSub.ready(),
    events: Events.find({}).fetch(),
  };
})(EventsTimeline);

