import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Container, Loader } from 'semantic-ui-react';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';

/** Renders a table containing all of the Stuff documents. Use <StuffItem> to render each row. */
class ManageLocationPage extends React.Component {

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    return (
      <Container >
        <h3 style={{ textAlign: 'center' }}>Manage Locations: Coming Soon!</h3>
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
