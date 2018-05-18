import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Button, Table, Grid } from 'semantic-ui-react';
import Moment from 'moment/moment';
import {
  Charts, ChartContainer, ChartRow, YAxis, LineChart, Resizable,
} from 'react-timeseries-charts';
import { TimeRange, TimeSeries } from 'pondjs';
import { CSVLink } from 'react-csv';

import { getBoxEvent } from '../../../api/box-events/BoxEventsCollectionMethods';
import { getEventData } from '../../../api/fs-files/FSFilesCollectionMethods';
import { OpqBoxes } from '../../../api/opq-boxes/OpqBoxesCollection';

/** Displays event details, including the waveform at the time of the event. */
class EventSummary extends React.Component {
  constructor(props) {
    super(props);

    const { event } = props;

    const start = event.target_event_start_timestamp_ms;
    const end = event.target_event_end_timestamp_ms;

    this.state = {
      waveforms: [],
      waveformsVisible: {},
      timeRange: new TimeRange(start, end),
      start,
      end,
    };
  }

  render() {
    const { event } = this.props;
    const { waveforms, waveformsVisible } = this.state;
    return (
      <Table key={event.event_id} celled stackable>
        <Table.Body>
          <Table.Row>
            <Table.Cell>
              <strong>Event ID:</strong> {event.event_id}
            </Table.Cell>
            <Table.Cell>
              <strong>Type: </strong> {event.type}
            </Table.Cell>
            <Table.Cell>
              <strong>Boxes triggered: </strong> {event.boxes_triggered}
            </Table.Cell>
            <Table.Cell>
              <strong>Started at: </strong>
              {Moment(event.target_event_start_timestamp_ms).format('MM/DD/YYYY HH:mm:ss')}
            </Table.Cell>
            <Table.Cell>
              <strong>Ended at: </strong>
              {Moment(event.target_event_end_timestamp_ms).format('MM/DD/YYYY HH:mm:ss')}
            </Table.Cell>
          </Table.Row>
          <Table.Row>
            <Table.Cell colSpan={5}>
              <strong>Waveform available for: </strong>
              {event.boxes_received.sort().map(boxID => (
                <Button key={boxID} toggle content={`Box ${boxID}`}
                        onClick={this.toggleWaveForm}
                        active={waveformsVisible[boxID]}/>
              ))}
              <br/>
              {waveforms.map(waveform => (waveformsVisible[waveform.boxID] ? (
                <Grid stackable key={waveform.boxID}>
                  <Grid.Column width={14}>
                    {this.renderChart(waveform)}
                  </Grid.Column>
                  <Grid.Column width={2}>
                    Download:<br/>
                    <Button as={CSVLink} content='CSV' size='small'
                            filename={`Event ${event.event_id} Box ${waveform.boxID}.csv`}
                            data={waveform.raw_voltages.map(item => [item])} />
                  </Grid.Column>
                </Grid>
              ) : ''))}
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      </Table>
    );
  }

  toggleWaveForm = (event, data) => {
    const eventID = this.props.event.event_id;
    const boxID = data.content.split(' ')[1];
    const { waveforms, waveformsVisible } = this.state;

    if (waveformsVisible[boxID] === undefined) {
      getBoxEvent.call({ event_id: eventID, box_id: boxID }, (error, boxEvent) => {
        if (error) console.log(error);
        else {
          getEventData.call({ filename: boxEvent.data_fs_filename }, (e, waveform) => {
            if (e) console.log(e);
            else {
              const calibration_constant = this.props.calibration_constants[boxID];
              const raw_voltages = waveform.map(raw_measurement => raw_measurement / calibration_constant);
              const timestamps = boxEvent.window_timestamps_ms;
              const timestampedVoltages = [];

              for (let i = 0; i < timestamps.length - 1; i++) {
                const start = timestamps[i];
                const end = timestamps[i + 1];
                const difference = end - start;
                const step = difference / 200;
                for (let n = 0; n < 200; n++) {
                  timestampedVoltages.push([start + (n * step), raw_voltages[(200 * i) + n]]);
                }
              }

              const series = new TimeSeries({
                name: 'waveform',
                columns: ['time', 'value'],
                points: timestampedVoltages,
              });

              waveforms.push({ boxID, series, raw_voltages });
              waveforms.sort((a, b) => a.boxID - b.boxID);
              waveformsVisible[boxID] = true;
              this.setState({ waveforms, waveformsVisible });
            }
          });
        }
      });
    } else {
      waveformsVisible[boxID] = !waveformsVisible[boxID];
      this.setState({ waveformsVisible });
    }
  };

  renderChart = waveform => {
    const { boxID, series } = waveform;
    const style = { value: { normal: { stroke: 'green' } } };
    return (
      <Resizable>
        <ChartContainer timeRange={this.state.timeRange} enablePanZoom minDuration={60000 * 3}
                        onTimeRangeChanged={timeRange => this.setState({ timeRange })}
                        minTime={new Date(this.state.start)} maxTime={new Date(this.state.end)}>
          <ChartRow height={100}>
            <YAxis id='voltage' format={n => n.toFixed(2)} label={`Box ${boxID}`} labelOffset={-10}
                   width={60} min={series.min()} max={series.max()}/>
            <Charts>
              <LineChart axis='voltage' series={series} style={style}/>
            </Charts>
          </ChartRow>
        </ChartContainer>
      </Resizable>
    );
  };
}

EventSummary.propTypes = {
  event: PropTypes.object.isRequired,
  calibration_constants: PropTypes.object.isRequired,
};

export default withTracker(() => {
  Meteor.subscribe('opq_boxes');
  return {
    calibration_constants: Object.assign(...OpqBoxes.find().fetch().map(box => (
      { [box.box_id]: box.calibration_constant }
    ))),
  };
})(EventSummary);
