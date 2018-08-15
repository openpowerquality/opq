import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withRouter, Link } from 'react-router-dom';
import { Bert } from 'meteor/themeteorchef:bert';
import { Loader, Segment, Container, Button } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import HiddenField from 'uniforms-semantic/HiddenField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import BoxSelector from '../../layouts/BoxSelector';

class EditUserPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedBoxes: BoxOwners.findBoxIdsWithOwner(this.props.doc.username),
    };
  }

  helpText = `
  <p>Add a new user.</p>
  `;

  /** On submit, check if usename exists, set password to 'foo, then call generic base.updateMethod. */
  submit(data) {
    const { docId, firstName, lastName, role, boxIds } = data;
    const user = UserProfiles.findByID(docId);
    const collectionName = UserProfiles.getCollectionName();
    const updateData = { id: user._id, firstName, lastName, role, boxIds };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  changeSelectedBoxes = (event, data) => {
    this.setState({ selectedBoxes: data.value.sort() });
  };

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form.
   */
  renderPage() {
    const roles = ['user', 'admin'];
    const boxIds = OpqBoxes.findBoxIds();
    const formSchema = new SimpleSchema({
      docId: String,
      firstName: String,
      lastName: String,
      role: { type: String, allowedValues: roles, defaultValue: 'user' },
      boxIds: Array,
      'boxIds.$': { type: String, allowedValues: boxIds },
    });
    this.props.doc.docId = this.props.id;
    return (
        <Container>
          <WidgetPanel title="Edit User" helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit} model={this.props.doc}>
              <Segment>
                <HiddenField name='docId'/>
                <AutoField name='firstName'/>
                <AutoField name='lastName'/>
                <AutoField name='role'/>
                <div className='required field'>
                  <label>Boxes</label>
                  <BoxSelector boxIDs={boxIds} onChange={this.changeSelectedBoxes}
                               value={this.state.selectedBoxes}/>
                </div>
                <HiddenField name='boxIds' value={this.state.selectedBoxes}/>
                <SubmitField value='Save Changes'/>
                <ErrorsField/>
              </Segment>
            </AutoForm>
            <Button attached='bottom' size='tiny' as={Link} to={'/admin/manage/user/'}>Back to Manage Users</Button>
          </WidgetPanel>
        </Container>
    );
  }
}

/** Uniforms adds 'model' to the props, which we use. */
EditUserPage.propTypes = {
  ready: PropTypes.bool.isRequired,
  doc: PropTypes.object,
  model: PropTypes.object,
  id: PropTypes.string,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  const boxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  const userID = match.params._id;

  return {
    ready: userProfilesSubscription.ready() && boxOwnersSubscription.ready() && boxesSubscription.ready(),
    doc: UserProfiles.findByID(userID),
    id: userID,
  };
})(withRouter(EditUserPage));
