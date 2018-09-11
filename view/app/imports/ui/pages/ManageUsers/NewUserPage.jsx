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
import { defineMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '../../../api/users/BoxOwnersCollection';
import BoxSelector from '../../layouts/BoxSelector';

class NewUserPage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      selectedBoxes: [],
    };
  }

  helpText = `
  <p>Add a new user.</p>
  `;

  /** On submit, check if usename exists, set password to 'foo, then call generic base.defineMethod. */
  submit(data) {
    const { username, firstName, lastName, role, boxIds } = data;
    const profile = UserProfiles.findOne({ username });
    // return if Username already exists
    if (profile) {
      Bert.alert({
        type: 'danger', style: 'growl-bottom-left',
        message: `Definition failed: ${'Username already exists'}`,
      });
      return;
    }
    const collectionName = UserProfiles.getCollectionName();
    // set default password to foo
    const password = 'foo';
    const definitionData = { username, password, firstName, lastName, role, boxIds };
    defineMethod.call({ collectionName, definitionData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Definition failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Definition succeeded' })));
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
      username: String,
      firstName: String,
      lastName: String,
      role: { type: String, allowedValues: roles, defaultValue: 'user' },
      boxIds: Array,
      'boxIds.$': { type: String, allowedValues: boxIds },
    });
    return (
        <Container>
          <WidgetPanel title="Add Box" helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit}>
              <Segment>
                <AutoField name='username'/>
                <AutoField name='firstName'/>
                <AutoField name='lastName'/>
                <AutoField name='role'/>
                <div className='required field'>
                  <label>Boxes</label>
                  <BoxSelector boxIDs={boxIds} onChange={this.changeSelectedBoxes}
                               value={this.state.selectedBoxes}/>
                </div>
                <HiddenField name='boxIds' value={this.state.selectedBoxes}/>
                <SubmitField value='Submit'/>
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
NewUserPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  const boxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());

  return {
    ready: userProfilesSubscription.ready() && boxOwnersSubscription.ready() && boxesSubscription.ready(),
  };
})(withRouter(NewUserPage));
