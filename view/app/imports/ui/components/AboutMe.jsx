import React from 'react';
import { Table, Input, Label, Dropdown, Icon, Button } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import NumberFormat from 'react-number-format';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import { Bert } from 'meteor/themeteorchef:bert';
import WidgetPanel from '../layouts/WidgetPanel';
import { UserProfiles } from '../../api/users/UserProfilesCollection';

/** Display user profile info. */
class AboutMe extends React.Component {

  constructor(props) {
    super(props);
    let phoneSms;
    let phoneNumber = '';
    // split phone field to separate the phone number from carrier
    if (this.props.phone !== undefined) {
      phoneSms = this.props.phone.substring(this.props.phone.indexOf('@'));
      phoneNumber = this.props.phone.substring(0, this.props.phone.indexOf('@'));
    }

    this.state = {
      editMode: false,
      phone: this.props.phone,
      sms: phoneSms,
      number: phoneNumber,
    };
  }

  helpText = `
  <p>Your profile information is displayed here.</p>
  `;

  /** Here's the system stats page. */
  render() {
    const divStyle = { paddingLeft: '10px' };
    const topPadding = { paddingTop: '20px' };
    const providers = [
      { text: 'Verizon', value: '@vtext.com' },
      { text: 'T-Mobile', value: '@tmomail.net' },
      { text: 'AT&T', value: '@txt.att.net' },
      { text: 'Sprint', value: '@messaging.sprintpcs.com' },
      { text: 'Virgin Mobile', value: '@vmobl.com' },
    ];
    return (
        <WidgetPanel title="About Me" helpText={this.helpText}>
          <Table style={divStyle} basic='very'>
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
              <Table.Row>
                <Table.Cell>Phone</Table.Cell>
                {this.state.editMode ? (
                    <Table.Cell>
                      <NumberFormat value={this.state.number}
                                    placeholder="+1 (___)___-____"
                                    customInput={Input}
                                    format="+1 (###) ###-####"
                                    mask="_"
                                    labelPosition='right'
                                    onValueChange={(values) => {
                                      const { value } = values;
                                      this.setState({ number: value });
                                    }}>
                        <input/>
                        <Label>
                          <Dropdown placeholder='Provider' options={providers}
                                    value={this.state.sms}
                                    onChange={this.changeSms}/>
                        </Label>
                      </NumberFormat>
                      <br/>
                      <Button.Group style={topPadding} size='mini'>
                        <Button onClick={this.disableEditing}>Cancel</Button>
                        <Button positive onClick={this.updatePhone}>Save</Button>
                      </Button.Group>
                    </Table.Cell>
                ) : (
                    <Table.Cell>
                      <NumberFormat value={this.state.number} displayType={'text'} format="+1 (###) ###-####"
                      >
                      </NumberFormat>
                      <Icon name='pencil' color='grey' onClick={this.enableEditing} style={divStyle}/>
                    </Table.Cell>
                )}
              </Table.Row>
            </Table.Body>
          </Table>
        </WidgetPanel>
    );
  }

  enableEditing = () => {
    this.setState({ editMode: true });
  };

  disableEditing = () => {
    this.setState({ editMode: false });
  };

  changePhoneNumber = (event, data) => {
    this.setState({ number: data.value });
  };

  changeSms = (event, data) => {
    this.setState({ sms: data.value });
  };

  /**
   * Concatenates the inputted phone number and user's carrier
   * Updates userProfile with new phone address
   */
  updatePhone = () => {
    const newPhone = this.state.number.concat(this.state.sms);
    const collectionName = UserProfiles.getCollectionName();
    const id = UserProfiles.findByUsername(this.props.username)._id;
    const updateData = { id, phone: newPhone };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  };
}

/** Require an array of Stuff documents in the props. */
AboutMe.propTypes = {
  firstName: PropTypes.string.isRequired,
  lastName: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
  role: PropTypes.string.isRequired,
  phone: PropTypes.string,
};

export default AboutMe;
