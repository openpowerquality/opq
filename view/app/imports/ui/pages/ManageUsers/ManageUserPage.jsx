import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { Container, Loader, Table, Button, Modal } from 'semantic-ui-react';
import { withRouter, Link } from 'react-router-dom';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import { removeMethod } from '../../../api/base/BaseCollection.methods';
import '../../components/Notifications/notificationStyle.css';

class ManageUserPage extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      selectedUser: '',
    };
  }

  removeUser = (event, data) => {
    const docID = UserProfiles.findByUsername(data.value)._id;
    const collectionName = UserProfiles.getCollectionName();
    removeMethod.call({ collectionName, docID }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Delete failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'User deleted' })));
    setTimeout(this.handleClose, 3000);
  };

  handleOpen = (event, data) => {
    this.setState({ selectedUser: data.value });
    this.setState({ modalOpen: true });
  };

  handleClose = () => this.setState({ modalOpen: false });

  helpText = `
  <p>Edit or delete OPQ users</p>
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
          <WidgetPanel title="Manage Users" helpText={this.helpText} noPadding>
            <Table>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Username</Table.HeaderCell>
                  <Table.HeaderCell>Name</Table.HeaderCell>
                  <Table.HeaderCell>Role</Table.HeaderCell>
                  <Table.HeaderCell>Box Ids</Table.HeaderCell>
                  <Table.HeaderCell></Table.HeaderCell>
                  <Table.HeaderCell></Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {users.map((user, index) => <Table.Row key={index}>
                  <Table.Cell>{user.username}</Table.Cell>
                  <Table.Cell>{user.firstName} {user.lastName}</Table.Cell>
                  <Table.Cell>{user.role}</Table.Cell>
                  <Table.Cell>{Array.from(BoxOwners.findBoxIdsWithOwner(user.username)).join(', ')}</Table.Cell>
                  <Table.Cell>
                    <Button size='tiny' as={Link} to={`/admin/manage/user/edit/${user._id.toHexString()}`}>
                      Edit
                    </Button>
                  </Table.Cell>
                  <Table.Cell>
                    <Button size='tiny' basic color='red' onClick={this.handleOpen}
                            value={user.username}>Delete</Button>
                  </Table.Cell>
                </Table.Row>)}
              </Table.Body>
              <Table.Footer fullWidth>
                <Table.Row>
                  <Table.HeaderCell colSpan='6'>
                    <Button size='tiny' as={Link} to={'/admin/manage/user/new'}>Create New User</Button>
                  </Table.HeaderCell>
                </Table.Row>
              </Table.Footer>
            </Table>
          </WidgetPanel>
          <Modal size='mini' open={this.state.modalOpen}>
            <Modal.Header>Are you sure?</Modal.Header>
            <Modal.Content>
              <p>Are you sure you want to delete {this.state.selectedUser}?</p>
              <Button className='red mini' content='Delete' value={this.state.selectedUser} onClick={this.removeUser}/>
              <Button size='mini' content='Cancel' onClick={this.handleClose}/>
            </Modal.Content>
          </Modal>
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
