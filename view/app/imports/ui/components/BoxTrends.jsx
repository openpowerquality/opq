import React from 'react';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Grid, Loader, Header, Dropdown, Checkbox } from 'semantic-ui-react';
import { LineChart } from 'react-chartkick';
import { Chart } from 'chart.js';
import { Calendar } from 'react-calendar';
import Moment from 'moment';

import { getBoxIDs } from '../../api/opq-boxes/OpqBoxesCollectionMethods';
import { dailyTrendsInRange } from '../../api/trends/TrendsCollectionMethods';
import WidgetPanel from '../layouts/WidgetPanel';

/** Displays data from the trends collection */
class BoxTrends extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      ready: false,
      boxIdOptions: [],
      selectedBoxes: ['1'],
      graph: 'voltage',
      viewingRange: [Moment().subtract(30, 'days').valueOf(), Moment().valueOf()],
      showMax: false,
      showMin: false,
      showAverage: true,
      trends: [],
    };

    getBoxIDs.call((error, boxIDs) => {
      if(error) console.log(error);
      else {
        const boxIdOptions = boxIDs.sort().map(boxID => ({
          text: `Box ${boxID}`,
          value: boxID,
        }));
        this.setState({
          boxIdOptions,
          ready: true,
        });
      }
    });

    dailyTrendsInRange.call({
      boxIDs: ['3', '5'],
      startDate_ms: this.state.viewingRange[0],
      endDate_ms: this.state.viewingRange[1],
    }, (error, data) => {
      if(error) console.log(error);
      else {
        this.setState({
          trends: data,
          ready: true,
        });
        console.log(this.state.trends);
      }
    });
  }

  render() {
    return this.state.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {

    return (
      <WidgetPanel title='Daily Trends'>
        <Grid container>
          <Grid.Row centered>

            <Grid.Column width={10}>
              <Calendar selectRange onChange={this.updateCalendar} />
            </Grid.Column>

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
              <Dropdown multiple search selection fluid
                        placeholder='Boxes to display'
                        options={this.state.boxIdOptions}
                        onChange={this.updateBoxIdDropdown}
                        defaultValue={this.state.selectedBoxes}
              />
            </Grid.Column>
          </Grid.Row>

          {this.state.selectedBoxes.map(boxID => (
            <Grid.Row centered key={`box${boxID}`}>
              <Grid.Column width={3}>
                <Header as='h4' content={`Box ${boxID}`} textAlign='center'/>
              </Grid.Column>
              <Grid.Column width={4}>
                <Checkbox toggle label='Max' onChange={this.changeChecked} checked={this.state.showMax}/>
              </Grid.Column>
              <Grid.Column width={4}>
                <Checkbox toggle label='Min' onChange={this.changeChecked} checked={this.state.showMin}/>
              </Grid.Column>
              <Grid.Column width={5}>
                <Checkbox toggle label='Average' onChange={this.changeChecked} checked={this.state.showAverage}/>
              </Grid.Column>
            </Grid.Row>
          ))}
          <Grid.Row>
            <Grid.Column>
              <LineChart data={{ '2017-05-13': 2, '2017-05-14': 5 }}/>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </WidgetPanel>
    );
  }

  updateBoxIdDropdown = (event, data) => {
    this.setState({ selectedBoxes: data.value });
  }

  changeGraph = (event, data) => {
    this.setState({ graph: data.value });
  }

  changeChecked = (event, data) => {
    switch (data.label) {
      case 'Max':
        this.setState({ showMax: !this.state.showMax });
        break;
      case 'Average':
        this.setState({ showAverage: !this.state.showAverage });
        break;
      case 'Min':
        this.setState({ showMin: !this.state.showMin });
        break;
      default:
        break;
    }
  }

  updateCalendar = data => {
    console.log(Moment(data[1]).diff(Moment(data[0]), 'days', true));
  }
}

/** No subscriptions, because the data is updated daily */
export default BoxTrends;
