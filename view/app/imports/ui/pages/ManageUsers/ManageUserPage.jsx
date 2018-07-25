import React from 'react';
import PropTypes from 'prop-types';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Container, Loader, Table, Button } from 'semantic-ui-react';
import { withRouter, Link } from 'react-router-dom';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';

class ManageUserPage extends React.Component {

  helpText = `
  <p>View all users</p>
  `;

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader active>Getting data</Loader>;
  }

  /** Render the page once subscriptions have been received. */
  renderPage() { // eslint-disable-line class-methods-use-this
    const usernames = UserProfiles.findUsernames();
    const users = usernames.map(username => UserProfiles.findByUsername(username));

    return (
        <Container>
          <WidgetPanel title="Manage Users" noPadding>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Username</Table.HeaderCell>
                  <Table.HeaderCell>Name</Table.HeaderCell>
                  <Table.HeaderCell>Role</Table.HeaderCell>
                  <Table.HeaderCell>Box Ids</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user, index) => <Table.Row key={index}>
                  <Table.Cell>{user.username}</Table.Cell>
                  <Table.Cell>{user.firstName} {user.lastName}</Table.Cell>
                  <Table.Cell>{user.role}</Table.Cell>
                  <Table.Cell>{Array.from(BoxOwners.findBoxIdsWithOwner(user.username)).join(', ')}</Table.Cell>
                </Table.Row>)}
              </Table.Body>
              <Table.Footer fullWidth>
                <Table.Row>
                  <Table.HeaderCell colSpan='5'>
                    <Button><Link to={'/admin/manage/user/new'}>Create New User</Link></Button>
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
ManageUserPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  return {
    ready: userProfilesSubscription.ready() && boxOwnersSubscription.ready(),
  };
})(withRouter(ManageUserPage));
