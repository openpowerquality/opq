import React from 'react';
import { Table } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import WidgetPanel from '../layouts/WidgetPanel';


/** Display user profile info. */
class AboutMe extends React.Component {

  /** Here's the system stats page. */
  render() {
    const divStyle = { paddingLeft: '10px' };
    return (
        <WidgetPanel title="About Me">
          <Table style={divStyle} basic='very' >
            <Table.Body>
              <Table.Row>
                <Table.Cell>Name</Table.Cell>
                <Table.Cell>{this.props.firstName} {this.props.lastName}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Username</Table.Cell>
                <Table.Cell>{this.props.username}</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>Role</Table.Cell>
                <Table.Cell>{this.props.role}</Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        </WidgetPanel>
    );
  }
}
/** Require an array of Stuff documents in the props. */
AboutMe.propTypes = {
  firstName: PropTypes.string.isRequired,
  lastName: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
  role: PropTypes.string.isRequired,
};

export default AboutMe;
