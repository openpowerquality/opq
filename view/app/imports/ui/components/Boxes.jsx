import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Card } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { SystemStats } from '/imports/api/system-stats/SystemStatsCollection';
import WidgetPanel from '../layouts/WidgetPanel';
import BoxCard from './BoxCard';

/* eslint max-len:0 */

/** Display the summary information for all Boxes passed in as a property. */
class Boxes extends React.Component {

  /** Render the Boxes as a group of Cards. */
  render() {
    const stats = SystemStats.findOne({});
    const boxTrendStats = stats ? stats.box_trend_stats : [];
    const divStyle = { paddingLeft: '10px', paddingRight: '10px' };
    return (
        <WidgetPanel title={this.props.title}>
          <Card.Group stackable style={divStyle} itemsPerRow={4}>
            {this.props.boxes.map((box) => <BoxCard key={box._id} box={box} admin={this.props.admin} boxTrendStats={boxTrendStats}/>)}
          </Card.Group>
        </WidgetPanel>
    );
  }
}
/** Require an array of Stuff documents in the props. */
Boxes.propTypes = {
  ready: PropTypes.bool.isRequired,
  boxes: PropTypes.array.isRequired,
  title: PropTypes.string.isRequired,
  admin: PropTypes.bool,
};


Boxes.getDefaultProps = {
  admin: false,
};


/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const systemStatsSub = Meteor.subscribe(SystemStats.getPublicationName());
  return {
    ready: systemStatsSub.ready(),
  };
})(Boxes);
