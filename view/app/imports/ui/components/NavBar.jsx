import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { withRouter, NavLink } from 'react-router-dom';
import { Menu, Image } from 'semantic-ui-react';

class NavBar extends React.Component {
  render() {
    const divStyle = { color: '#2185D0', paddingLeft: '2px', fontWeight: 'bold' };
    return (
      <Menu stackable borderless>
        <Menu.Item as={NavLink} exact to="/">
          <Image width="20px" src="/images/opqlogo.png"/>
          <div style={divStyle}>OPQView</div>
        </Menu.Item>
        <Menu.Item position="right" as={NavLink} exact to="/aboutus"><div style={divStyle}>About Us</div></Menu.Item>
        {this.props.currentUser === '' ? (
          <Menu.Item as={NavLink} exact to="/signin"><div style={divStyle}>Login</div></Menu.Item>
        ) : (
          <Menu.Item as={NavLink} exact to="/signout"><div style={divStyle}>Logout</div></Menu.Item>
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
