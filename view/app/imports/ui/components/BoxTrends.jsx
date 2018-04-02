import React from 'react';
import { Grid, Header, Dropdown, Checkbox, Popup, Input, Button } from 'semantic-ui-react';
import Moment from 'moment';
import Calendar from 'react-calendar'; // eslint-disable-line no-unused-vars
import {
  FlexibleXYPlot,
  LineMarkSeries,
  LineSeries,
  XAxis,
  YAxis,
  DiscreteColorLegend,
} from 'react-vis';
import 'react-vis/dist/style.css';

// import {
//   Charts,
//   ChartContainer,
//   ChartRow,
//   YAxis,
//   LineChart,
//   Baseline,
//   Resizable,
//   Legend,
//   styler,
//   TimeAxis,
// } from 'react-timeseries-charts';
// import { TimeRange, TimeSeries } from 'pondjs';

import { getBoxIDs } from '../../api/opq-boxes/OpqBoxesCollectionMethods';
import { dailyTrendsInRange } from '../../api/trends/TrendsCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';

const colors = [
  '#e6194b',
  '#3cb44b',
  '#ffe119',
  '#0082c8',
  '#f58231',
  '#911eb4',
  '#46f0f0',
  '#f032e6',
  '#d2f53c',
  '#fabebe',
  '#008080',
  '#e6beff',
  '#aa6e28',
  '#fffac8',
  '#800000',
  '#aaffc3',
  '#808000',
  '#ffd8b1',
  '#000080',
];

/** Displays data from the trends collection */
class BoxTrends extends React.Component {
  constructor(props) {
    super(props);

    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 7);

    this.state = {
      ready: false,
      boxIdOptions: [],
      selectedBoxes: ['1'],
      field: 'voltage',
      start,
      end,
      linesToShow: ['Box 1 average'],
      lineColors: {
        'Box 1 average': colors[0],
      },
      trendData: {},
      colorCounter: 1,
    };
  }

  initialize = () => {
    getBoxIDs.call((error, boxIDs) => {
      if (error) console.log(error);
      else {
        const boxIdOptions = boxIDs.sort().map(boxID => ({
          text: `Box ${boxID}`,
          value: boxID,
        }));

        dailyTrendsInRange.call({
          boxIDs: this.state.selectedBoxes,
          startDate_ms: this.state.start.getTime(),
          endDate_ms: this.state.end.getTime(),
        }, (err, trendData) => {
          if (err) console.log(err);
          else {
            this.setState({
              trendData,
              boxIdOptions,
              ready: true,
            });
          }
        });
      }
    });
  };

  render() {
    if (!this.state.ready) this.initialize(); // Need to initialize somehow because there are no subs
    return this.state.ready ? this.renderPage() : '';
  }

  renderPage() {
    return (
      <WidgetPanel title='Daily Trends'>
        <Grid container>
          {this.fieldBoxPicker()}
          {this.datePicker()}
          <Grid.Row>{this.state.selectedBoxes.map(boxID => this.checkboxes(boxID))}</Grid.Row>
          {this.generateGraph()}
        </Grid>
      </WidgetPanel>
    );
  }


  fieldBoxPicker = () => (
    <Grid.Row centered>
      <Grid.Column width={6}>
        <Dropdown search selection fluid
                  placeholder='Graph to display'
                  options={[
                    { text: 'Voltage', value: 'voltage' },
                    { text: 'Frequency', value: 'frequency' },
                    { text: 'THD', value: 'thd' },
                  ]}
                  onChange={this.changeGraph}
                  defaultValue={this.state.field}
        />
      </Grid.Column>
      <Grid.Column width={10}>
        <Dropdown multiple search selection fluid
                  placeholder='Boxes to display'
                  options={this.state.boxIdOptions}
                  onChange={this.updateBoxIdDropdown}
                  defaultValue={this.state.selectedBoxes}
        />
      </Grid.Column>
    </Grid.Row>
  );

  changeGraph = (event, data) => {
    this.setState({ field: data.value });
  };

  updateBoxIdDropdown = (event, data) => {
    const selectedBoxes = data.value.sort();
    this.setState({ selectedBoxes }, () => {
      const linesToShow = this.state.linesToShow;
      linesToShow.forEach((label, index) => {
        const boxID = label.split(' ')[1];
        console.log(this.state.selectedBoxes.includes(boxID));
        if (!this.state.selectedBoxes.includes(boxID)){
          console.log(`removing ${label}`);
          linesToShow.splice(index, 1);
        }
      });
      this.setState({ linesToShow });
    });
  };


  datePicker = () => (
    <Grid.Row><Grid.Column><Grid stackable>
      <Grid.Row>
        <Grid.Column width={6}>
          <Popup on='focus'
                 trigger={
                   <Input fluid placeholder='Input a starting date'
                          value={Moment(this.state.start).format('MM/DD/YYYY')}
                          label='Start'
                   />
                 }
                 content={<Calendar onChange={this.changeStart} value={this.state.start}/>}
          />
        </Grid.Column>
        <Grid.Column width={6}>
          <Popup on='focus'
                 trigger={
                   <Input fluid placeholder='Input an ending date'
                          value={Moment(this.state.end).format('MM/DD/YYYY')}
                          label='End'
                   />
                 }
                 content={<Calendar onChange={this.changeEnd} value={this.state.end}/>}
          />
        </Grid.Column>
        <Grid.Column width={4}>
          <Button content='Fetch data' fluid onClick={this.getData}/>
        </Grid.Column>
      </Grid.Row>
    </Grid></Grid.Column></Grid.Row>
  );

  changeStart = start => {
    this.setState({ start });
  };

  changeEnd = end => {
    this.setState({ end });
  };

  getData = () => {
    dailyTrendsInRange.call({
      boxIDs: this.state.selectedBoxes,
      startDate_ms: this.state.start.getTime(),
      endDate_ms: this.state.end.getTime(),
    }, (error, trendData) => {
      if (error) console.log(error);
      else this.setState({ trendData });
    });
  };


  checkboxes = (boxID) => (
    <Grid.Column width={8} key={`box${boxID}`}>
      <Grid verticalAlign='middle'>
        <Grid.Row centered>
          <Grid.Column width={4}>
            <Header as='h5' content={`Box ${boxID}`}/>
          </Grid.Column>
          <Grid.Column width={4}>
            Average
            <Checkbox toggle id={`Box ${boxID} average`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} average`)}
            />
          </Grid.Column>
          <Grid.Column width={4}>
            Max
            <Checkbox toggle id={`Box ${boxID} max`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} max`)}
            />
          </Grid.Column>
          <Grid.Column width={4}>
            Min
            <Checkbox toggle id={`Box ${boxID} min`}
                      onChange={this.changeChecked}
                      checked={this.state.linesToShow.includes(`Box ${boxID} min`)}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Grid.Column>
  );

  changeChecked = (event, props) => {
    // If we have it in the list, remove it. Otherwise, add it.
    let linesToShow = this.state.linesToShow;
    if (linesToShow.includes(props.id)) linesToShow = linesToShow.filter(label => label !== props.id);
    else linesToShow.push(props.id);
    linesToShow.sort();
    let lineColors = this.state.lineColors;
    if (!lineColors[props.id]) lineColors[props.id] = colors[this.state.colorCounter];
    this.setState({ linesToShow, lineColors, colorCounter: this.state.colorCounter + 1 });
  };


  generateGraph = () => {
    const graphData = this.getGraphData();
    const referenceData = this.generateReference();
    return (
      <Grid.Row>
        <Grid.Column width={16}>
          <DiscreteColorLegend
            orientation='horizontal'
            items={this.state.linesToShow.map(label => ({
              title: label,
              color: this.state.lineColors[label],
            }))}
          />
          <FlexibleXYPlot height={300}>
            <XAxis tickFormat={(timestamp) => Moment(timestamp).format('MM/DD')}/>
            <YAxis/>
            <LineSeries strokeDasharray='5 5' color='lightgrey' data={referenceData[0].data}/>
            <LineSeries strokeDasharray='5 5' color='grey' data={referenceData[1].data}/>
            <LineSeries strokeDasharray='5 5' color='lightgrey' data={referenceData[2].data}/>
            {graphData.map(set => <LineMarkSeries key={set.label} data={set.data} size={2}
                                                  color={this.state.lineColors[set.label]}
            />)}
          </FlexibleXYPlot>
        </Grid.Column>
      </Grid.Row>
    )
  };

  getGraphData = () => {
    const trendData = this.state.trendData;
    const field = this.state.field;
    const linesToShow = this.state.linesToShow;
    const graphData = linesToShow.map(label => {
      const [, boxID, stat] = label.split(' ');
      let data = [];
      if (trendData[boxID]) {
        const boxData = trendData[boxID].dailyTrends;
        data = Object.keys(boxData).filter(timestamp => boxData[timestamp][field]).map(timestamp => ({
          x: parseInt(timestamp, 10),
          y: boxData[timestamp][field][stat],
        }));
      }
      return { label, data };
    });
    return graphData;
  };

  generateReference = () => {
    let references;
    switch (this.state.field) {
      case 'voltage':
        references = [114, 120, 126];
        break;
      case 'frequency':
        references = [57, 60, 63];
        break;
      case 'thd':
        references = [null, 0, 0.1];
        break;
      default:
        break;
    }
    return references.map(value => ({
      label: value,
      data: [
        { x: this.state.start.getTime(), y: value },
        { x: this.state.end.getTime(), y: value },
      ],
    }));
  };

  // getGraphData = () => {
  //   const trendData = this.state.trendData;
  //   const field = this.state.field;
  //   const linesToShow = this.state.linesToShow;
  //   const graphData = linesToShow.map(label => {
  //     const [, boxID, stat] = label.split(' ');
  //     let data = [];
  //     if (trendData[boxID]) {
  //       const boxData = trendData[boxID].dailyTrends;
  //       data = Object.keys(boxData).filter(timestamp => boxData[timestamp][field]).map(timestamp => ([
  //         timestamp,
  //         boxData[timestamp][field][stat],
  //       ]));
  //     }
  //     return { label, data };
  //   });
  //   return graphData;
  // };
  //
  // generateReference = () => {
  //   let references;
  //   switch (this.state.field) {
  //     case 'voltage':
  //       references = [114, 120, 126];
  //       break;
  //     case 'frequency':
  //       references = [57, 60, 63];
  //       break;
  //     case 'thd':
  //       references = [null, 0, 0.1];
  //       break;
  //     default:
  //       break;
  //   }
  //   return references;
  // };
  //
  // generateGraph = () => {
  //   const field = this.state.field;
  //   const graphData = this.getGraphData();
  //   const timeRange = new TimeRange([this.state.start, this.state.end]);
  //   const reference = this.generateReference();
  //   const style = styler(this.state.linesToShow.map(label => ({
  //     key: label,
  //     color: this.state.lineColors[label],
  //   })));
  //   const wholeDataSet = [];
  //   graphData.forEach(set => {
  //     set.data.forEach(point => {
  //       wholeDataSet.push(point[1]);
  //     });
  //   });
  //   reference.forEach(value => {
  //     wholeDataSet.push(value);
  //   });
  //
  //   const legend = this.state.linesToShow.map(label => ({
  //     key: label,
  //     label,
  //   }));
  //
  //   return (
  //     <Grid.Row>
  //       <Grid.Column width={16}>
  //         <Legend type='swatch' align='left' categories={legend}
  //                 style={style}/>
  //         <Resizable>
  //           <ChartContainer timeRange={timeRange} enablePanZoom
  //                           timeAxisTickCount={8}>
  //             <ChartRow height="300">
  //               <YAxis
  //                 id={field}
  //                 min={Math.min(...wholeDataSet)}
  //                 max={Math.max(...wholeDataSet)}
  //                 format={n => n.toFixed(2)}
  //               />
  //               <Charts>
  //                 {graphData.map(set => {
  //                   const series = new TimeSeries({
  //                     name: set.label,
  //                     columns: ['time', 'value'],
  //                     points: set.data,
  //                   });
  //                   return <LineChart
  //                     key={set.label} axis={field} series={series}
  //                     style={{ value: { normal: { stroke: this.state.lineColors[set.label] } } }}
  //                   />;
  //                 })}
  //                 <Baseline
  //                   axis={field} style={{ line: { stroke: 'grey' } }}
  //                   value={reference[1]} label="Nominal" position="right"
  //                 />
  //                 <Baseline
  //                   axis={field} style={{ line: { stroke: 'lightgrey' } }}
  //                   value={reference[2]} label="+5%" position="right"
  //                 />
  //                 <Baseline
  //                   axis={field} style={{ line: { stroke: 'lightgrey' } }}
  //                   value={reference[0]} label="-5%" position="right"
  //                   visible={field !== 'thd'}
  //                 />
  //               </Charts>
  //             </ChartRow>
  //           </ChartContainer>
  //         </Resizable>
  //       </Grid.Column>
  //     </Grid.Row>
  //   );
  // };
}

// No subscriptions, because the data is updated daily
export default BoxTrends;
