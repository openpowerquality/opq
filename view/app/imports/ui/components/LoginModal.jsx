import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Modal, Menu } from 'semantic-ui-react';
import SimpleSchema from 'simpl-schema';
import { NavLink } from 'react-router-dom';

import LoginForm from './LoginForm';

const userSimpleSchema = new SimpleSchema({
  email: {
    type: String,
  },
  password: {
    type: String,
  },
});

class LoginModal extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      email: '',
      error: '',
    };
    this.login = this.login.bind(this);
    this.logout = this.logout.bind(this);
  }
  login(mod){
    console.log('login');
    const email = mod.email;
    const password = mod.password;
    Meteor.loginWithPassword(email, password, (error) => {
      this.setState({ error: error });
    });
    this.setState({ email: email });
  }
  logout(){
    console.log('logout');
    Meteor.logout();
    this.setState({
      email: '',
      error: '',
    });
  }
  render() {
    return (
      <Modal size="mini" trigger={<Menu.Item>Login</Menu.Item>}>
        <Modal.Content>
          <LoginForm schema={userSimpleSchema} onSubmit={this.login}/>
        </Modal.Content>
      </Modal>
    );
  }
}

LoginModal.proptypes = {
  currentUser: PropTypes.string,
};

export default withTracker(() => ({
  currentUser: Meteor.user() ? Meteor.user().username : '',
}))(LoginModal);
