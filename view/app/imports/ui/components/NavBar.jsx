import React from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from 'semantic-ui-react';

import LoginLogout from './LoginLogout';

const NavBar = () => {
  return (
    <Menu widths={3} stackable>
      <Menu.Item header as={NavLink} exact to="/">OPQView</Menu.Item>
      <Menu.Item as={NavLink} exact to="/aboutus">About Us</Menu.Item>
      <LoginLogout as={NavLink} exact to="#"/>
    </Menu>
  );
}

export default NavBar;
