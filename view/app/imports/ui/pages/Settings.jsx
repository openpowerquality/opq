import React from 'react';
import { Header, Image } from 'semantic-ui-react';

class Settings extends React.Component {
  render() {
    return (
      <Header as="h2" textAlign="center">
        <Image src="/ftlogo.png" />
        <p>Settings</p>
      </Header>
    );
  }
}
export default Settings;
