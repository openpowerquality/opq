import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { withRouter, NavLink } from 'react-router-dom';
import { Menu, Image } from 'semantic-ui-react';

class NavBar extends React.Component {
  render() {
    return (
      <Menu stackable borderless>
        <Menu.Item as={NavLink} exact to="/"><Image width="20px" src="/images/opqlogo.png"/>&nbsp;OPQView</Menu.Item>
        <Menu.Item position="right" as={NavLink} exact to="/aboutus">About Us</Menu.Item>
        {this.props.currentUser === '' ? (
          <Menu.Item as={NavLink} exact to="/signin">Login</Menu.Item>
        ) : (
          <Menu.Item as={NavLink} exact to="/signout">Logout</Menu.Item>
        )}
      </Menu>
    );
  }
}

NavBar.propTypes = {
  currentUser: PropTypes.string,
};

const NavBarContainer = withTracker(() => ({
  currentUser: Meteor.user() ? Meteor.user().username : '',
}))(NavBar);
export default withRouter(NavBarContainer);
