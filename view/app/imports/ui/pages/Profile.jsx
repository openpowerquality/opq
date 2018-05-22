import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Container, Loader } from 'semantic-ui-react';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import AboutMe from '/imports/ui/components/AboutMe';
import Boxes from '/imports/ui/components/Boxes';
import { _ } from 'lodash';

/** Renders a table containing all of the Stuff documents. Use <StuffItem> to render each row. */
class Profile extends React.Component {

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const username = Meteor.user().username;
    const { firstName, lastName, role } = UserProfiles.findByUsername(username);
    const boxIds = BoxOwners.findBoxIdsWithOwner(username);
    const boxes = _.sortBy(boxIds.map(id => OpqBoxes.findBox(id)), doc => doc.box_id);
    return (
      <Container >
        <AboutMe firstName={firstName} lastName={lastName} username={username} role={role}/>
        <Boxes title="My Boxes" boxes={boxes} />
      </Container>
    );
  }
}

/** Require an array of Stuff documents in the props. */
Profile.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get access to Stuff documents.
  const profilesSub = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSub = Meteor.subscribe(BoxOwners.getPublicationName());
  const opqBoxesSub = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    ready: profilesSub.ready() && boxOwnersSub.ready() && opqBoxesSub.ready(),
  };
})(Profile);
