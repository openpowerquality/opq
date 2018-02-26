import React from 'react';
import { NavLink } from 'react-router-dom';
import { Menu } from 'semantic-ui-react';

import LoginDropDown from './LoginDropDown';
import LoginModal from './LoginModal';

const NavBar = () => {
  return (
    <Menu widths={3} stackable>
      <Menu.Item header as={NavLink} exact to="/">OPQView</Menu.Item>
      <Menu.Item as={NavLink} exact to="/aboutus">About Us</Menu.Item>
      <Menu.Item as={LoginModal} />
    </Menu>
  );
}

export default NavBar;
