import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Container, Loader } from 'semantic-ui-react';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import AboutMe from '/imports/ui/components/AboutMe';
import MyBoxes from '/imports/ui/components/MyBoxes';

/** Renders a table containing all of the Stuff documents. Use <StuffItem> to render each row. */
class UserProfilePage extends React.Component {

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const username = Meteor.user().username;
    const { firstName, lastName, role } = UserProfiles.findByUsername(username);
    const boxIds = BoxOwners.findBoxIdsWithOwner(username);
    const boxes = boxIds.map(id => OpqBoxes.findBox(id));
    return (
      <Container >
        <AboutMe firstName={firstName} lastName={lastName} username={username} role={role}/>
        <MyBoxes boxes={boxes}/>
      </Container>
    );
  }
}

/** Require an array of Stuff documents in the props. */
UserProfilePage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to Stuff documents.
  const profilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    ready: profilesSubscription.ready() && boxOwnersSubscription.ready() && opqBoxesSubscription.ready(),
  };
})(UserProfilePage);
