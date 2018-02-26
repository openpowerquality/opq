import { Meteor } from 'meteor/meteor';
import React from 'react';
import { Dropdown, Message } from 'semantic-ui-react';
import SimpleSchema from 'simpl-schema';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';

import LoginForm from './LoginForm';

const schema = new SimpleSchema({
  email: {
    type: String,
  },
  password: {
    type: String,
  },
});

class LoginDropDown extends React.Component {
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
    this.setState({
      email: email,
    });
    Meteor.loginWithPassword(email, password, (err) => {
      if (err) {
        this.setState({
          error: err.reason,
        });
      } else {
        this.setState({
          error: '',
        });
      }
    });
  }

  logout() {
    this.setState({
      email: '',
      error: '',
    });
    Meteor.logout();
  }

  render() {
    return this.props.currentUser === '' ? (
      <Dropdown item text="Login">
        <Dropdown.Menu>
          <Dropdown.Item onClick={this.keepVisible}>
            <LoginForm schema={schema} onSubmit={this.login} />
            {this.state.error === '' ? '' : (
              <Message error header="Login was not successful"
                       content={this.state.error} />
            )}
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    ) : (
      <Dropdown item text={this.props.currentUser} icon={'user'}>
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

LoginDropDown.proptypes = {
  currentUser: PropTypes.string,
};

export default withTracker(() => ({
  currentUser: Meteor.user() ? Meteor.user().username : '',
}))(LoginDropDown);
