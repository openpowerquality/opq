import React from 'react';
import { Meteor } from 'meteor/meteor';
import { withRouter, Link } from 'react-router-dom';
import { Loader, Table, Button, Container } from 'semantic-ui-react';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';

/** Renders a table containing all of the Stuff documents. Use <StuffItem> to render each row. */
class ManageLocationPage extends React.Component {

  helpText = `
  <p>Lists all current OPQ Locations</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const locations = Locations.getDocs();

    return (
        <Container>
          <WidgetPanel title="Manage OPQ Locations" helpText={this.helpText} noPadding>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Slug</Table.HeaderCell>
                  <Table.HeaderCell>Location</Table.HeaderCell>
                  <Table.HeaderCell>Coordinates</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {locations.map((location, index) => <Table.Row key={index}>
                  <Table.Cell>{location.slug}</Table.Cell>
                  <Table.Cell>{location.description}</Table.Cell>
                  <Table.Cell>{location.coordinates[0]}, {location.coordinates[1]}</Table.Cell>
                  <Table.Cell>
                    <Button size='tiny'><Link to={`/admin/manage/location/edit/${location._id}`}>Edit</Link></Button>
                  </Table.Cell>
                </Table.Row>)}
              </Table.Body>
              <Table.Footer fullWidth>
                <Table.Row>
                  <Table.HeaderCell colSpan='5'>
                    <Button><Link to={'/admin/manage/location/new'}>Add OPQ Location</Link></Button>
                  </Table.HeaderCell>
                </Table.Row>
              </Table.Footer>
            </Table>
          </WidgetPanel>
        </Container>
    );
  }
}

/** Require the ready flag. */
ManageLocationPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to Stuff documents.
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: locationsSubscription.ready(),
  };
})(ManageLocationPage);
