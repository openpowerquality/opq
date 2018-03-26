import React from 'react';
import { Table } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import WidgetPanel from '../layouts/WidgetPanel';
import MyBox from './MyBox';

/** Display user profile info. */
class MyBoxes extends React.Component {

  /** Here's the system stats page. */
  render() {
    return (
        <WidgetPanel title="My Boxes">
          <Table celled>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell>Box ID</Table.HeaderCell>
                <Table.HeaderCell>Name</Table.HeaderCell>
                <Table.HeaderCell>Description</Table.HeaderCell>
                <Table.HeaderCell>Calibration Constant</Table.HeaderCell>
                <Table.HeaderCell>Location(s)</Table.HeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {this.props.boxes.map((box) => <MyBox key={box._id} box={box} />)}
            </Table.Body>
          </Table>
        </WidgetPanel>
    );
  }
}
/** Require an array of Stuff documents in the props. */
MyBoxes.propTypes = {
  boxes: PropTypes.array.isRequired,
};

export default MyBoxes;
