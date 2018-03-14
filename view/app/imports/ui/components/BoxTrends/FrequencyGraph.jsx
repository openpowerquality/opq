import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Header, Grid, Loader, Checkbox, Container } from 'semantic-ui-react';

/*
 * !!!! THIS FILE IS CURRENTLY NOT BEING USED !!!!
 * It is being kept for reference purposes
 */

import { Trends } from '/imports/api/trends/TrendsCollection.js';

class FrequencyGraph extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      boxIDs: ['1'],
      showMax: false,
      showAverage: true,
      showMin: false,
    };

    this.updateGraph = this.updateGraph.bind(this);
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    const boxIDs = this.props.boxesToDisplay;
    const type = this.props.type;
    const frequencies = {};
    boxIDs.forEach(boxID => {
      frequencies[boxID] = {};
      frequencies[boxID].data = this.props.trends.filter(trend => {
        return trend.box_id === boxID;
      }).map(trend => ({
        max: trend.frequency.max.toFixed(2),
        average: trend.frequency.average.toFixed(2),
        min: trend.frequency.min.toFixed(2),
        timestamp_ms: trend.timestamp_ms,
      }));
    });

    // Get the max and min values for the graph's X axis

    // Get the max and min values for the graph's Y axis
    boxIDs.forEach(boxID => {
      frequencies[boxID].highest = Math.max(...frequencies[boxID].data.map(frequency => frequency.max));
      frequencies[boxID].lowest = Math.min(...frequencies[boxID].data.map(frequency => frequency.min));
    });

    return (
      <Container>

      </Container>
    );
  }

  updateGraph(event, data) {
    switch (data.label) {
      case 'Max': this.setState({ showMax: !this.state.showMax }); break;
      case 'Average': this.setState({ showAverage: !this.state.showAverage }); break;
      case 'Min': this.setState({ showMin: !this.state.showMin }); break;
      default: break;
    }
  }
}

FrequencyGraph.propTypes = {
  ready: PropTypes.bool.isRequired,
  trends: PropTypes.array,
  boxes: PropTypes.array,
  type: PropTypes.string,
};

export default withTracker(() => {
  const trendsSub = Meteor.subscribe('get_recent_trends', { numTrends: 120 });
  const trends = Trends.find().fetch();
  return {
    ready: trendsSub.ready(),
    trends,
  };
})(FrequencyGraph);
