import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Modal, Item } from 'semantic-ui-react';
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
  }
  login(mod){
    const email = mod.email;
    const password = mod.password;
    Meteor.loginWithPassword(email, password, (error) => {
      this.setState({ error: error ? error : '' });
    });
    this.setState({ email: email });
  }
  logout(){
    Meteor.logout();
    this.setState({
      email: '',
      error: '',
    });
  }
  render() {
    return (
      <Modal trigger={<NavLink>Login</NavLink>}>
        <Modal.Content>
          <LoginForm schema={userSimpleSchema} email={/>
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
