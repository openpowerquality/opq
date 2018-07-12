import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { withRouter } from 'react-router-dom';
import { Container, Segment } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import HiddenField from 'uniforms-semantic/HiddenField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { Notifications } from '/imports/api/notifications/NotificationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';

class NotificationManager extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      formChange: false,
    };
  }

  helpText = `
  <p>Edit an OPQ Box definition.</p>
  <p>Click 'Back to Manage OPQ Boxes' to return to the listing page.</p>
  `;

  /** On submit, look up location slug from description, then call generic base.updateMethod. */
  submit(data) {
    const { username, notification_pref, notifications } = data;
    console.log(notifications);
    const collectionName = UserProfiles.getCollectionName();
    const id = UserProfiles.findByUsername(username)._id;
    const updateData = { id, notification_pref, notifications };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
    console.log(UserProfiles.findByUsername(username));
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form. Convert location slugs (from doc) into descriptions for display.
   */
  render() {
    const sendingFrequency = ['once a day', 'once an hour', 'never'];
    const types = Notifications.notificationTypes;

    const formSchema = new SimpleSchema({
      username: String,
      notifications: { type: Array, required: false },
      'notifications.$': {
        type: String,
        allowedValues: types,
      },
      notification_pref: { type: Object, label: 'Messaging Preferences' },
      'notification_pref.text': { type: Boolean, required: false },
      'notification_pref.email': { type: Boolean, required: false },
      'notification_pref.max_sent_per_day': {
        type: String,
        label: 'Send me notifications:',
        allowedValues: sendingFrequency,
      },
    });
    // Update the Uniforms model with current values for locationDescription and Owners.
    return (
        <Container>
          <WidgetPanel title='Manage Notifications' helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit} onChange={this.revealSaveButton}
                      model={this.props.doc}>
              <Segment>
                <HiddenField name='username'/>
                <AutoField name='notifications'/>
                <AutoField name='notification_pref'/>
                {this.state.formChange ? (
                    <SubmitField value='Save Changes' className='green mini'/>
                ) : ''}
                <ErrorsField/>
              </Segment>
            </AutoForm>
          </WidgetPanel>
        </Container>
    );
  }

  revealSaveButton = () => {
    this.setState({ formChange: true });
  };
}

/** Uniforms adds 'model' to the props, which we use. */
NotificationManager.propTypes = {
  doc: PropTypes.object,
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :_id.
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const username = Meteor.user().username;
  return {
    ready: userProfilesSubscription.ready(),
    doc: UserProfiles.findByUsername(username),
  };
})(withRouter(NotificationManager));
