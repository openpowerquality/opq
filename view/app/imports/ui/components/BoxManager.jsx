import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Header, Table, Grid, Segment, Icon, Loader } from 'semantic-ui-react';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection.js';
import PanelWrapper from '../components/PanelWrapper.jsx';

class BoxManager extends React.Component {
  listUnownedOpqBoxes() {
    return this.props.opqBoxes.map(box => <p key={box._id}>{JSON.stringify(box, null, 2)}</p>);
  }

  opqBoxRow() {
    return this.props.opqBoxes.map(box => (
        <Table.Row key={box._id._str}>
          <Table.Cell>{box.box_id}</Table.Cell>
          <Table.Cell>{box.name}</Table.Cell>
          <Table.Cell>{box.description}</Table.Cell>
          <Table.Cell>{box.calibration_constant}</Table.Cell>
          <Table.Cell>{box.location}</Table.Cell>
        </Table.Row>
    ));
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Loading...</Loader>;
  }

  renderPage() {
    return (
        <Grid stackable padded columns={2}>
          <Grid.Column>
            <PanelWrapper headerText='OPQ Boxes' headerIcon='power'>
              <Table celled>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Box ID</Table.HeaderCell>
                    <Table.HeaderCell>Name</Table.HeaderCell>
                    <Table.HeaderCell>Description</Table.HeaderCell>
                    <Table.HeaderCell>Calibration Constant</Table.HeaderCell>
                    <Table.HeaderCell>Location</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>

                <Table.Body>
                  {this.opqBoxRow()}
                </Table.Body>
              </Table>
            </PanelWrapper>
          </Grid.Column>

          <Grid.Column>
            <PanelWrapper headerText='Subscribed Data' headerIcon='book'>
              <Header as='h3'>Unowned Boxes</Header>
              {this.listUnownedOpqBoxes()}
            </PanelWrapper>
          </Grid.Column>
        </Grid>
    );
  }
}

BoxManager.propTypes = {
  opqBoxes: PropTypes.array,
  ready: PropTypes.bool.isRequired,
};

export default BoxManager = withTracker(() => { // eslint-disable-line no-class-assign
  const opqBoxesHandle = Meteor.subscribe(OpqBoxes.publicationNames.GET_USER_UNOWNED_BOXES);

  return {
    opqBoxes: OpqBoxes.find().fetch(),
    ready: opqBoxesHandle.ready(),
  };
})(BoxManager);
