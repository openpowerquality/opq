import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { Grid, Header, Button, Modal } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { Notifications } from '/imports/api/notifications/NotificationsCollection';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import { sendTestEmail } from '/imports/api/email/email.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
// Modal has a bug where it appears slightly offscreen, fixed with custom css
import './notificationStyle.css';

class NotificationManager extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      formChange: false,
      modalOpen: false,
    };
  }

  helpText = `
  <p>Edit your notification settings here.</p>`;

  /** On submit call generic base.updateMethod to update user's notification preferences */
  submit(data) {
    const { notification_preferences } = data;
    const collectionName = UserProfiles.getCollectionName();
    const id = data._id;
    const updateData = { id, notification_preferences };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Edits saved' })));
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form
   */
  render() {
    const sendingFrequency = ['once a day', 'once an hour', 'never'];
    const types = Notifications.notificationTypes;
    const headerStyle = { paddingBottom: '14px' };
    const paddedStyle = { paddingRight: '14px', paddingLeft: '14px' };

    const formSchema = new SimpleSchema({
      notification_preferences: { type: Object },
      'notification_preferences.text': { type: Boolean, required: false },
      'notification_preferences.email': { type: Boolean, required: false },
      'notification_preferences.notification_types': { type: Array, required: false, label: false },
      'notification_preferences.notification_types.$': {
        type: String,
        allowedValues: types,
      },
      'notification_preferences.max_per_day': {
        type: String,
        allowedValues: sendingFrequency,
        label: false,
      },
    });

    // Update the Uniforms model with current values for UserProfile
    return (
        <WidgetPanel title='Manage Notifications' helpText={this.helpText} noPadding>
          <AutoForm schema={formSchema} onChange={this.revealSaveButton} onSubmit={this.submit}
                    model={this.props.doc} style={paddedStyle}>
            <Grid padded columns={3} stackable celled='internally' id='ntf-settings'>
              <Grid.Column>
                <Grid.Row>
                  <Header style={headerStyle} size='tiny'>My Notifications:</Header>
                </Grid.Row>
                <Grid.Row>
                  <AutoField name='notification_preferences.notification_types'/>
                </Grid.Row>
              </Grid.Column>
              <Grid.Column>
                <Grid.Row>
                  <Header style={headerStyle} size='tiny'>Send me notifications:</Header>
                </Grid.Row>
                <AutoField name='notification_preferences.max_per_day'/>
              </Grid.Column>
              <Grid.Column>
                <Grid.Row>
                  <Header style={headerStyle} size='tiny'>Notify me by:</Header>
                </Grid.Row>
                <AutoField name='notification_preferences.text'/>
                <AutoField name='notification_preferences.email'/>
                <Button size='mini' content='Send a test message' onClick={this.handleOpen}/>
              </Grid.Column>
              {this.state.formChange ? (
                  <Grid.Row>
                    <Grid.Column>
                      <SubmitField value='Save changes' className='green mini'/>
                    </Grid.Column>
                  </Grid.Row>
              ) : ''}
            </Grid>
            <ErrorsField/>
          </AutoForm>
          <Modal size='mini' open={this.state.modalOpen}>
            <Modal.Header>Are you sure?</Modal.Header>
            <Modal.Content>
              <p>Click OK to send a test message, or Cancel to exit.</p>
              <Button className='green mini' content='OK' onClick={this.messageTest}/>
              <Button size='mini' content='Cancel' onClick={this.handleClose}/>
            </Modal.Content>
          </Modal>
        </WidgetPanel>
    );
  }

  revealSaveButton = () => this.setState({ formChange: true });

  handleOpen = () => this.setState({ modalOpen: true });

  handleClose = () => this.setState({ modalOpen: false });

  /** Sends an email to user's updated recipients */
  messageTest = () => {
    const recipients = UserProfiles.getRecipients(this.props.doc._id);
    sendTestEmail.call({ recipients }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Message send failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Message sent' })));
    setTimeout(this.handleClose, 4000);
  }
}

/** Uniforms adds 'model' to the props */
NotificationManager.propTypes = {
  doc: PropTypes.object.isRequired,
  model: PropTypes.object,
};

export default NotificationManager;

