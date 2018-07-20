import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { withRouter } from 'react-router-dom';
import { Container, Grid, Header, Button, Modal } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { Notifications } from '/imports/api/notifications/NotificationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import { sendTestEmail } from '/imports/api/email/email.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
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

  /** On submit, look up location slug from description, then call generic base.updateMethod. */
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
   * Create a custom schema for the form. Convert location slugs (from doc) into descriptions for display.
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
        <Container>
          <WidgetPanel title='Manage Notifications' helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit} onChange={this.revealSaveButton}
                      model={this.props.doc} style={paddedStyle}>
              <Grid padded columns={3} stackable celled='internally'>
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
                    <Header style={headerStyle} size='tiny'>Notify me by:</Header>
                  </Grid.Row>
                  <AutoField name='notification_preferences.text'/>
                  <AutoField name='notification_preferences.email'/>
                </Grid.Column>
                <Grid.Column>
                  <Grid.Row>
                    <Header style={headerStyle} size='tiny'>Send me notifications:</Header>
                  </Grid.Row>
                  <AutoField name='notification_preferences.max_per_day'/>
                </Grid.Column>
                {this.state.formChange ? (
                    <Grid.Row>
                      <Grid.Column>
                        <SubmitField value='Save changes' className='green mini'/>
                        <Button size='mini' content='Save and Test' onClick={this.handleOpen}/>
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
        </Container>
    );
  }

  revealSaveButton = () => this.setState({ formChange: true });

  handleOpen = () => this.setState({ modalOpen: true });

  handleClose = () => this.setState({ modalOpen: false });

  messageTest = () => {
    const recipients = UserProfiles.getRecipients(this.props.doc);
    sendTestEmail.call({ recipients }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Message send failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Message sent' })));
    setTimeout(this.handleClose, 4000);
  }
}

/** Uniforms adds 'model' to the props, which we use. */
NotificationManager.propTypes = {
  doc: PropTypes.object.isRequired,
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const username = Meteor.user().username;
  return {
    ready: userProfilesSubscription.ready(),
    doc: UserProfiles.findByUsername(username),
  };
})(withRouter(NotificationManager));

