import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Modal, Menu, Dropdown, Message } from 'semantic-ui-react';
import SimpleSchema from 'simpl-schema';

import LoginForm from './LoginForm';

const userSimpleSchema = new SimpleSchema({
  email: {
    type: String,
  },
  password: {
    type: String,
  },
});

class LoginLogout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      error: '',
    };
    this.login = this.login.bind(this);
    this.logout = this.logout.bind(this);
  }
  login(mod) {
    const email = mod.email;
    const password = mod.password;
    Meteor.loginWithPassword(email, password, (error) => {
      if (error) {
        this.setState({
          email: '',
          error: error.reason,
        });
      } else {
        this.setState({
          email: mod.email,
          error: '',
        });
      }
    });
    console.log(this.state);
  }
  logout() {
    Meteor.logout();
    this.setState({
      email: '',
      error: '',
    });
    console.log(this.state);
  }
  render() {
    return this.props.currentUser === '' ? (
      <Modal size="mini" trigger={<Menu.Item>Login</Menu.Item>}>
        <Modal.Content>
          <LoginForm schema={userSimpleSchema} onSubmit={this.login}/>
          {this.state.error === '' ? '' : (
            <Message error header="Login failed"
                     content={this.state.error} />
          )}
        </Modal.Content>
      </Modal>
    ) : (
      <Dropdown item text={this.state.email} icon={'user'}>
        <Dropdown.Menu>
          <Dropdown.Item
            icon="sign out"
            text="Log Out"
            onClick={this.logout}
          />
        </Dropdown.Menu>
      </Dropdown>
    );
  }
}

LoginLogout.proptypes = {
  currentUser: PropTypes.string,
};

export default withTracker(() => ({
  currentUser: Meteor.user() ? Meteor.user().username : '',
}))(LoginLogout);
