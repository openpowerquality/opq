import React from 'react';
import { Header, Image } from 'semantic-ui-react';

const NotFound = () => (
  <Header as="h2" textAlign="center">
    <Image src="/ftlogo.png" />
    <p>Page not found</p>
  </Header>
);

export default NotFound;
