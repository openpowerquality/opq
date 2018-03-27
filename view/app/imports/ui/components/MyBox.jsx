import React from 'react';
import { Table } from 'semantic-ui-react';
import PropTypes from 'prop-types';

/** Renders a single row in the MyBoxes table. */
class MyBox extends React.Component {
  render() {
    return (
      <Table.Row>
        <Table.Cell>{this.props.box.box_id}</Table.Cell>
        <Table.Cell>{this.props.box.name}</Table.Cell>
        <Table.Cell>{this.props.box.description}</Table.Cell>
        <Table.Cell>{this.props.box.calibration_constant}</Table.Cell>
        <Table.Cell>{JSON.stringify(this.props.box.locations)}</Table.Cell>
      </Table.Row>
    );
  }
}

/** Require a document to be passed to this component. */
MyBox.propTypes = {
  box: PropTypes.object.isRequired,
};

export default MyBox;
