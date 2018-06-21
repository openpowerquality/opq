import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Container, Loader } from 'semantic-ui-react';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';

/** Renders a table containing all of the Stuff documents. Use <StuffItem> to render each row. */
class ManageUserPage extends React.Component {

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    return (
      <Container >
        <h3 style={{ textAlign: 'center' }}>Manage Users: Coming Soon!</h3>
      </Container>
    );
  }
}

/** Require the ready flag. */
ManageUserPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to Stuff documents.
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  return {
    ready: userProfilesSubscription.ready(),
  };
})(ManageUserPage);
