import React from 'react';
import { Grid, Loader, Header, Dropdown, Checkbox, Popup, Input, Button } from 'semantic-ui-react';
import Moment from 'moment';
import Calendar from 'react-calendar'; // eslint-disable-line no-unused-vars
import { FlexibleXYPlot, LineMarkSeries, XAxis, YAxis, VerticalGridLines, HorizontalGridLines } from 'react-vis';
import 'react-vis/dist/style.css';

import { getBoxIDs } from '../../api/opq-boxes/OpqBoxesCollectionMethods';
import { dailyTrendsInRange } from '../../api/trends/TrendsCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';

/** Displays data from the trends collection */
class BoxTrends extends React.Component {
  constructor(props) {
    super(props);

    const start = new Date();
    start.setDate(1);
    const end = new Date();

    this.state = {
      ready: false,
      boxIdOptions: [],
      selectedBoxes: ['1', '5', '3'],
      graph: 'voltage',
      start,
      end,
      linesToShow: ['Box 1 average'],
      trendData: {},
    };
  }

  initialize = () => {
    getBoxIDs.call((error, boxIDs) => {
      if (error) console.log(error);
      else {
        const boxIdOptions = boxIDs.map(boxID => ({
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
    return this.state.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    const trendData = this.state.trendData;
    const field = this.state.graph;
    const linesToShow = this.state.linesToShow;
    const graphData = linesToShow.map(label => {
      const [, boxID, stat] = label.split(' ');
      const boxData = trendData[boxID].dailyTrends;
      const data = Object.keys(boxData).filter(timestamp => boxData[timestamp][field]).map(timestamp => ({
        x: new Date(parseInt(timestamp, 10)),
        y: boxData[timestamp][field][stat],
      }));
      return { label, data };
    });
    console.log(graphData);

    return (
      <WidgetPanel title='Daily Trends'>
        <Grid container>
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
                        defaultValue={this.state.graph}
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

          {this.state.selectedBoxes.map(boxID => (
            <Grid.Row centered key={`box${boxID}`}>
              <Grid.Column width={3}>
                <Header as='h4' content={`Box ${boxID}`} textAlign='center'/>
              </Grid.Column>
              <Grid.Column width={4}>
                <Checkbox toggle label='Max' id={`Box ${boxID} max`}
                          onChange={this.changeChecked}
                          checked={this.state.linesToShow.includes(`Box ${boxID} max`)}
                />
              </Grid.Column>
              <Grid.Column width={4}>
                <Checkbox toggle label='Min' id={`Box ${boxID} min`}
                          onChange={this.changeChecked}
                          checked={this.state.linesToShow.includes(`Box ${boxID} min`)}
                />
              </Grid.Column>
              <Grid.Column width={5}>
                <Checkbox toggle label='Average' id={`Box ${boxID} average`}
                          onChange={this.changeChecked}
                          checked={this.state.linesToShow.includes(`Box ${boxID} average`)}
                />
              </Grid.Column>
            </Grid.Row>
          ))}
          {}
          <Grid.Row>
            <Grid.Column width={16}>
              <FlexibleXYPlot height={300}>
                <XAxis/>
                <YAxis/>
                <VerticalGridLines />
                <HorizontalGridLines />
                {graphData.map(set => (
                  <LineMarkSeries key={set.label} data={set.data}/>
                ))}
              </FlexibleXYPlot>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </WidgetPanel>
    );
  }

  changeGraph = (event, data) => {
    this.setState({ graph: data.value });
  };

  updateBoxIdDropdown = (event, data) => {
    this.setState({ selectedBoxes: data.value });
  };

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
  }

  changeChecked = (event, props) => {
    // If we have it in the list, remove it. Otherwise, add it.
    let linesToShow = this.state.linesToShow;
    if (linesToShow.includes(props.id)) linesToShow = linesToShow.filter(label => label !== props.id);
    else linesToShow.push(props.id);
    this.setState({ linesToShow });
  };


}

// No subscriptions, because the data is updated daily
export default BoxTrends;
