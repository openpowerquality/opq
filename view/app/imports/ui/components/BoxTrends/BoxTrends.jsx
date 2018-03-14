import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Loader, Container, Segment, Header, Dropdown } from 'semantic-ui-react';

import { getBoxIDs } from '/imports/api/opq-boxes/OpqBoxesCollectionMethods.js';
import VoltageGraph from './VoltageGraph.jsx';

class BoxTrends extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      boxIDs: [],
      boxIdOptions: [],
      selectedBoxes: [],
    };

    getBoxIDs.call((error, boxIDs) => {
      if (error) {
        console.log(error);
      } else {
        this.setState({
          boxIDs,
          boxIdOptions: boxIDs.sort().map(ID => ({
            text: `Box ${ID}`,
            value: ID,
          })),
        });
      }
    });
    this.updateBoxIdDropdown = this.updateBoxIdDropdown.bind(this);
  }

  render() {
    return this.props.ready ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    return (
      <Container>
        <Segment attached='top'>
          <Header as='h3' icon='line chart' content='Trends' floated='left' />
          <Dropdown placeholder='Boxes to display' multiple search selection
                    options={this.state.boxIdOptions}
                    onChange={this.updateBoxIdDropdown}
                    defaultValue={['1']} />
        </Segment>
        <Segment attached='bottom'>
          <VoltageGraph boxesToDisplay={this.state.selectedBoxes}/>
        </Segment>
      </Container>
    );
  }

  updateBoxIdDropdown(event, data) {
    this.setState({
      selectedBoxes: data.value,
    });
  }
}

BoxTrends.propTypes = {
  ready: PropTypes.bool.isRequired,
  currentUser: PropTypes.string.isRequired,
};

export default withTracker(() => {
  const trendsSubscription = Meteor.subscribe('get_recent_trends', { numTrends: 20 });
  return {
    ready: trendsSubscription.ready(),
    currentUser: Meteor.user() ? Meteor.user.currentUser : '',
  };
})(BoxTrends);
