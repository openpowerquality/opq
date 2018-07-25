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
    let carrierString;
    let numberString = '';
    // split phone field to separate the phone number from carrier
    if (this.props.phone !== undefined) {
      carrierString = this.props.phone.substring(this.props.phone.indexOf('@'));
      numberString = this.props.phone.substring(1, this.props.phone.indexOf('@'));
    }

    this.state = {
      editMode: false,
      carrier: carrierString,
      phoneNumber: numberString,
      oldPhoneNumber: numberString,
      oldCarrier: carrierString,
    };
  }

  helpText = `
  <p>Your profile information is displayed here.</p>
  `;

  /** Here's the system stats page. */
  render() {
    const divStyle = { paddingLeft: '10px' };
    const textStyle = { color: '#808080', display: 'inline' };
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
                      <NumberFormat value={this.state.phoneNumber}
                                    placeholder="+1 (___)___-____"
                                    customInput={Input}
                                    format="+1 (###) ###-####"
                                    mask="_"
                                    labelPosition='right'
                                    onValueChange={(values) => {
                                      const { value } = values;
                                      this.setState({ phoneNumber: value });
                                    }}>
                        <input/>
                        <Label>
                          <Dropdown placeholder='Provider' options={providers}
                                    value={this.state.carrier}
                                    onChange={this.changeCarrier}
                          />
                        </Label>
                      </NumberFormat>
                      <br/>
                      <Button.Group style={topPadding} size='mini'>
                        <Button onClick={this.disableEditing}>Cancel</Button>
                        <Button positive
                                disabled={this.state.phoneNumber.length !== 10 || this.state.carrier === undefined}
                                onClick={this.updatePhone}>Save</Button>
                      </Button.Group>
                    </Table.Cell>
                ) : (
                    <Table.Cell>
                      {this.state.phoneNumber === '' ?
                          (<p style={textStyle}>None</p>) :
                          (<NumberFormat value={this.state.phoneNumber} displayType={'text'}
                                         format="+1 (###) ###-####"/>)}
                      <Icon name='pencil' color='grey' onClick={this.enableEditing} style={divStyle}/>
                    </Table.Cell>
                )}
              </Table.Row>
            </Table.Body>
          </Table>
        </WidgetPanel>
    );
  }

  enableEditing = () => this.setState({ editMode: true });

  disableEditing = () =>
      this.setState({
        editMode: false,
        carrier: this.state.oldCarrier,
        phoneNumber: this.state.oldPhoneNumber,
      });

  changeCarrier = (event, data) => this.setState({ carrier: data.value });

  /**
   * Concatenates the inputted phone number and chosen carrier
   * Updates userProfile with new phone address
   * If update is successful, states of oldPhoneNumber and oldCarrier are updated as well so that
   * the new values are displayed when user cancels out of edit mode
   */
  updatePhone = () => {
    const usTrunkCode = '1';
    const newPhone = usTrunkCode.concat(this.state.phoneNumber, this.state.carrier);
    const collectionName = UserProfiles.getCollectionName();
    const id = this.props.id;
    const updateData = { id, phone: newPhone };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        (Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' }),
            this.setState({
              oldPhoneNumber: this.state.phoneNumber,
              oldCarrier: this.state.carrier,
            }))));
  };
}

/** Require an array of Stuff documents in the props. */
AboutMe.propTypes = {
  firstName: PropTypes.string.isRequired,
  lastName: PropTypes.string.isRequired,
  username: PropTypes.string.isRequired,
  role: PropTypes.string.isRequired,
  phone: PropTypes.string,
  id: PropTypes.object.isRequired,
};

export default AboutMe;
