import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { NavLink, withRouter, Redirect } from 'react-router-dom';
import { withTracker } from 'meteor/react-meteor-data';
import { Menu } from 'semantic-ui-react';

const NavBar = (props) => (
  <Menu widths={3} stackable>
    <Menu.Item as={NavLink} exact to="/"><strong>OPQView</strong></Menu.Item>
    <Menu.Item as={NavLink} exact to="/aboutus">About Us</Menu.Item>
    {props.currentUser === '' ? (
      <Menu.Item as={NavLink} exact to="/signin">Login</Menu.Item>
    ) : (
      <Menu.Item as={NavLink} exact to="/signout">Logout</Menu.Item>
    )}
  </Menu>
);

NavBar.propTypes = {
  currentUser: PropTypes.string,
};


const NavBarContainer = withTracker(() => ({
  currentUser: Meteor.user() ? Meteor.user().username : '',
}))(NavBar);
export default withRouter(NavBarContainer);
