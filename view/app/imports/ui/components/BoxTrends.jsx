import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Meteor } from 'meteor/meteor';
import { Grid, Header, Dropdown, Checkbox, Popup, Input, Button, Loader } from 'semantic-ui-react';
import Moment from 'moment';
import Calendar from 'react-calendar';
import {
  Charts, ChartContainer, ChartRow, YAxis, LineChart, Baseline, Resizable, Legend, styler,
} from 'react-timeseries-charts';
import { TimeRange, TimeSeries } from 'pondjs';

import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';
import { dailyTrends } from '../../api/trends/TrendsCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';

const colors = [ // Colors get used in this order when a user toggles a toggler.
  '#3cb44b',
  '#ffe119',
  '#0082c8',
  '#f58231',
  '#911eb4',
  '#46f0f0',
  '#f032e6',
  '#008080',
  '#e6beff',
  '#aa6e28',
  '#fffac8',
  '#800000',
  '#808000',
  '#000080',
  '#ffd8b1',
  '#aaffc3',
  '#e6194b',
  '#d2f53c',
  '#fabebe',
];

/** Displays data from the trends collection */
class BoxTrends extends React.Component {
  constructor(props) {
    super(props);

    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);

    this.state = {
      selectedBoxes: [],
      start,
      end,
      linesToShow: [],
      lineColors: {},
      trendData: {},
      colorCounter: 0,
      timeRange: new TimeRange([start, end]),
      showGraph: false,
      field: '',
      loading: false,
    };
  }

  helpText = `
  <p>Box Trends uses Trend data to show changes in frequency, voltage, or THD for one or more boxes over time.</p>
  
  <p>Measurement: select either voltage, frequency, or THD.</p>
  
  <p>Boxes: select one or more boxes whose values you wish to graph over time. Once you specify a box, you will
  be able to specify whether you want to graph its maximum, minimum, or average value of the measurement. </p>
  
  <p>Start and End: Specify the start and end date for the visualization.</p>
  
  <p>Fetch Data: Click this button to see the visualization</p>
  
  <p>This visualization supports panning and zooming.  Scroll the mouse up or down over the visualization to change
  the time interval. Click and drag right or left to change the window of time displayed.</p>
  `;

  render() { return this.props.ready ? this.renderPage() : ''; }

  renderPage = () => (
    <WidgetPanel title='Box Trends' helpText={this.helpText}>
      <Grid container>
        {this.fieldBoxPicker()}
        {this.datePicker()}
        <Grid.Row>{this.state.selectedBoxes.map(boxID => this.checkboxes(boxID))}</Grid.Row>
        {this.state.loading ? <Grid.Row><Loader active content='Fetching data'/></Grid.Row> : ''}
        {this.state.showGraph ? this.generateGraph() : ''}
      </Grid>
    </WidgetPanel>
  );


  fieldBoxPicker = () => (
    <Grid.Row centered>
      <Grid.Column width={6}>
        <Dropdown search selection fluid
                  placeholder='Measurement to display'
                  options={[
                    { text: 'Voltage', value: 'voltage' },
                    { text: 'Frequency', value: 'frequency' },
                    { text: 'THD', value: 'thd' },
                  ]}
                  onChange={this.changeGraph}/>
      </Grid.Column>
      <Grid.Column width={10}>
        <Dropdown multiple search selection fluid
                  placeholder='Boxes to display'
                  options={this.props.boxIDs.map(boxID => ({ text: `Box ${boxID}`, value: boxID }))}
                  onChange={this.updateBoxIdDropdown}
                  defaultValue={this.state.selectedBoxes}/>
      </Grid.Column>
    </Grid.Row>
  );

  changeGraph = (event, data) => { this.setState({ field: data.value }); };

  updateBoxIdDropdown = (event, data) => {
    const selectedBoxes = data.value.sort();
    this.setState({ selectedBoxes }, () => {
      const linesShown = this.state.linesToShow;
      const linesToShow = linesShown.filter(label => {
        const boxID = label.split(' ')[1];
        return this.state.selectedBoxes.includes(boxID);
      });
      this.setState({ linesToShow });
      if (linesToShow.length === 0) this.setState({ showGraph: false });
    });
  };


  datePicker = () => (
    <Grid.Row><Grid.Column><Grid stackable>
      <Grid.Row>
        <Grid.Column width={6}>
          <Popup on='focus'
                 trigger={<Input fluid placeholder='Input a starting date'
                                 value={Moment(this.state.start).format('MM/DD/YYYY')}
                                 label='Start'/>}
                 content={<Calendar onChange={this.changeStart} value={this.state.start}/>}/>
        </Grid.Column>
        <Grid.Column width={6}>
          <Popup on='focus'
                 trigger={<Input fluid placeholder='Input an ending date'
                                 value={Moment(this.state.end).format('MM/DD/YYYY')}
                                 label='End'/>}
                 content={<Calendar onChange={this.changeEnd} value={this.state.end}/>}/>
        </Grid.Column>
        <Grid.Column width={4}>
          <Button content='Fetch data' fluid onClick={this.getData}/>
        </Grid.Column>
      </Grid.Row>
    </Grid></Grid.Column></Grid.Row>
  );

  changeStart = start => { this.setState({ start }); };
  changeEnd = end => { this.setState({ end }); };

  getData = () => {
    this.setState({ loading: true });
    if (this.state.selectedBoxes.length === 0 || this.state.field === '') return;
    dailyTrends.call({
      boxIDs: this.state.selectedBoxes,
      startDate_ms: this.state.start.getTime(),
      endDate_ms: this.state.end.getTime(),
    }, (error, trendData) => {
      if (error) console.log(error);
      else this.setState({ trendData, showGraph: this.state.linesToShow.length > 0, loading: false });
    });
    this.setState({ timeRange: new TimeRange([this.state.start, this.state.end]) });
  };


  checkboxes = boxID => (
    <Grid.Column width={8} key={`box${boxID}`}>
      <Grid verticalAlign='middle'>
        <Grid.Row centered>
          <Grid.Column width={3}>
            <Header as='h5' content={`Box ${boxID}`}/>
          </Grid.Column>
          <Grid.Column width={4}>
            Avg<br/>
            <Checkbox toggle id={`Box ${boxID} avg`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} avg`)}/>
          </Grid.Column>
          <Grid.Column width={4}>
            Max<br/>
            <Checkbox toggle id={`Box ${boxID} max`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} max`)}/>
          </Grid.Column>
          <Grid.Column width={5}>
            Min<br/>
            <Checkbox toggle id={`Box ${boxID} min`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} min`)}/>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Grid.Column>
  );

  changeChecked = (event, props) => {
    let linesToShow = this.state.linesToShow;
    if (linesToShow.includes(props.id)) linesToShow = linesToShow.filter(label => label !== props.id);
    else linesToShow.push(props.id);
    linesToShow.sort();
    const lineColors = this.state.lineColors;
    if (!lineColors[props.id]) lineColors[props.id] = colors[this.state.colorCounter];
    const showGraph = linesToShow.length > 0 && Object.keys(this.state.trendData).length > 0;
    this.setState({ linesToShow, lineColors, colorCounter: this.state.colorCounter + 1, showGraph });
  };


  generateGraph = () => {
    const field = this.state.field;
    const graphData = this.getGraphData();
    const reference = this.generateReference();

    const legend = this.state.linesToShow.map(label => ({ key: label, label }));
    const legendStyle = styler(this.state.linesToShow.map(label => (
      { key: label, color: this.state.lineColors[label] })));

    const wholeDataSet = [];
    graphData.forEach(set => { set.data.forEach(point => { wholeDataSet.push(point[1]); }); });
    reference.forEach(value => { wholeDataSet.push(value); });

    return (
      <Grid.Row>
        <Grid.Column width={16}>
          <Legend type='swatch' align='left' categories={legend} style={legendStyle}/>
          <Resizable>
            <ChartContainer timeRange={this.state.timeRange} enablePanZoom
                            onTimeRangeChanged={timeRange => this.setState({ timeRange })}
                            minTime={this.state.start} maxTime={this.state.end} minDuration={86400000 * 3}>
              <ChartRow height='300'>
                <YAxis id={field} format={n => n.toFixed(2)}
                       min={Math.min(...wholeDataSet)} max={Math.max(...wholeDataSet)}/>
                <Charts>
                  {graphData.map(set => {
                    const series = new TimeSeries({
                      name: set.label,
                      columns: ['time', 'value'],
                      points: set.data,
                    });
                    const style = { value: { normal: { stroke: this.state.lineColors[set.label], strokeWidth: 2 } } };
                    return <LineChart key={set.label} axis={field} series={series} style={style}/>;
                  })}
                  <Baseline axis={field} style={{ line: { stroke: 'grey' } }}
                            value={reference[1]} label='Nominal' position='right'/>
                  <Baseline axis={field} style={{ line: { stroke: 'lightgrey' } }}
                            value={reference[2]} label='+5%' position='right'/>
                  <Baseline axis={field} style={{ line: { stroke: 'lightgrey' } }}
                            value={reference[0]} label='-5%' position='right' visible={field !== 'thd'}/>
                </Charts>
              </ChartRow>
            </ChartContainer>
          </Resizable>
        </Grid.Column>
      </Grid.Row>
    );
  };

  getGraphData = () => {
    const trendData = this.state.trendData;
    const field = this.state.field;
    const linesToShow = this.state.linesToShow;
    return linesToShow.map(label => {
      const boxID = label.split(' ')[1];
      const stat = label.split(' ')[2] === 'avg' ? 'average' : label.split(' ')[2];
      let data = [];
      if (trendData[boxID]) {
        const boxData = trendData[boxID];
        data = Object.keys(boxData).filter(timestamp => boxData[timestamp][field]).map(timestamp => ([
          timestamp,
          boxData[timestamp][field][stat],
        ]));
      }
      return { label, data };
    });
  };

  generateReference = () => {
    let references;
    // @formatter:off
    switch (this.state.field) {
      case 'voltage': references = [114, 120, 126]; break;
      case 'frequency': references = [57, 60, 63]; break;
      case 'thd': references = [null, 0, 0.1]; break;
      default: break;
    }
    // @formatter: on
    return references;
  };
}

BoxTrends.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxIDs: PropTypes.array.isRequired,
};


export default withTracker(() => {
  const sub = Meteor.subscribe(OpqBoxes.publicationNames.GET_OPQ_BOXES);
  return { ready: sub.ready(), boxIDs: OpqBoxes.find().fetch().map(box => box.box_id).sort() };
})(BoxTrends);
