import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import { withRouter, NavLink } from 'react-router-dom';
import { Menu, Image, Dropdown, Icon, Popup } from 'semantic-ui-react';
import { Roles } from 'meteor/alanning:roles';
import NotificationViewer from './NotificationViewer';
import { ROLE } from '../../api/opq/Role';

/* eslint max-len: 0 */
class NavBar extends React.Component {
  render() {
    const divStyle = { color: '#2185D0', paddingLeft: '2px', fontWeight: 'bold' };

    return (
        <Menu stackable borderless>
          <Menu.Item as={NavLink} exact to="/">
            <Image width="20px" src="/images/opqlogo.png"/>
            <div style={divStyle}>OPQView</div>
          </Menu.Item>

          {this.props.currentUser ? (
              <Menu.Item as={NavLink} activeClassName="active" exact to="/profile" key='profile'>
                <div style={divStyle}>Profile</div>
              </Menu.Item>
          ) : ''}

          {this.props.currentUser ? (
              <Menu.Item as={NavLink} activeClassName="active" exact to="/livedata" key='livedata'>
                <div style={divStyle}>Live Data</div>
              </Menu.Item>
          ) : ''}

          {this.props.currentUser ? (
              <Menu.Item as={NavLink} activeClassName="active" exact to="/inspector" key='inspector'>
                <div style={divStyle}>Inspector</div>
              </Menu.Item>
          ) : ''}

          {this.props.currentUser ? (
              <Menu.Item as={NavLink} activeClassName="active" exact to="/boxmap" key='boxmap'>
                <div style={divStyle}>Box Map</div>
              </Menu.Item>
          ) : ''}

          {Roles.userIsInRole(Meteor.userId(), ROLE.ADMIN) ? (
              <Menu.Item as={NavLink} activeClassName="active" exact to="/admin" key='admin'>
                <div style={divStyle}>Admin</div>
              </Menu.Item>
          ) : ''}

          {this.props.currentUser ? (
              <Menu.Item>
                <NotificationViewer/>
              </Menu.Item>
          ) : ''}

          <Menu.Item position="right" as={NavLink} exact to="/about">
            <div style={divStyle}>About OPQ</div>
          </Menu.Item>

          <Menu.Item>
            {this.props.currentUser === '' ? (
                <Dropdown text="Login" pointing="top right" style={divStyle}>
                  <Dropdown.Menu>
                    <Dropdown.Item key="signin" icon="user" text="Sign In" as={NavLink} exact to="/signin"/>
                  </Dropdown.Menu>
                </Dropdown>
            ) : (
                <Dropdown text={this.props.currentUser} pointing="top right" style={divStyle}>
                  <Dropdown.Menu>
                    <Dropdown.Item icon="sign out" text="Sign Out" as={NavLink} exact to="/signout"/>
                  </Dropdown.Menu>
                </Dropdown>
            )}
          </Menu.Item>

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
