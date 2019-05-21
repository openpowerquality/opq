import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { withRouter, Link } from 'react-router-dom';
import { Container, Loader, Segment, Button } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import HiddenField from 'uniforms-semantic/HiddenField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { BoxOwners } from '/imports/api/users/BoxOwnersCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';
import { MakaiConfig } from '/imports/api/makai-config/MakaiConfigCollection';

class EditBoxPage extends React.Component {

  helpText = `
  <p>Edit an OPQ Box definition.</p>
  <p>Click 'Back to Manage OPQ Boxes' to return to the listing page.</p>
  `;

  /** On submit, look up location slug from description, then call generic base.updateMethod. */
  submit(data) {
    const { _id, name, description, calibration_constant, unplugged, locationDescription, owners } = data;
    const location = Locations.findSlugFromDescription(locationDescription);
    const collectionName = OpqBoxes.getCollectionName();
    const updateData = { id: _id, name, description, calibration_constant, unplugged, location, owners };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form. Convert location slugs (from doc) into descriptions for display.
   */
  renderPage() {
    const locationDescriptions = Locations.getDocs().map(doc => doc.description);
    const owners = UserProfiles.findUsernames(true);
    const formSchema = new SimpleSchema({
      box_id: String,
      name: String,
      description: String,
      owners: { type: Array },
      'owners.$': { type: String, allowedValues: owners },
      unplugged: Boolean,
      calibration_constant: Number,
      referenceFrequency: Number,
      referenceVoltage: Number,
      threshold_percent_f_low: Number,
      threshold_percent_f_high: Number,
      threshold_percent_v_low: Number,
      threshold_percent_v_high: Number,
      threshold_percent_thd_high: Number,
      locationDescription: { type: String, allowedValues: locationDescriptions, label: 'Location' },
    });
    // Update the Uniforms model with current values for locationDescription and Owners.
    this.props.doc.locationDescription = Locations.getDoc(this.props.doc.location).description;
    this.props.doc.owners = BoxOwners.findOwnersWithBoxId(this.props.doc.box_id);
    // Merge the threshold document from the database with the current this.props.doc. This will insert all fields in
    // the DB model into the doc model.
    Object.assign(this.props.doc, MakaiConfig.getTriggeringOverrideOrDefault(this.props.doc.box_id));
    return (
      <Container>
        <WidgetPanel title="Edit Box" helpText={this.helpText} noPadding>
          <AutoForm schema={formSchema} onSubmit={this.submit} model={this.props.doc}>
            <Segment>
              <HiddenField name='box_id'/>
              <AutoField name='name'/>
              <AutoField name='description'/>
              <AutoField name='unplugged'/>
              <AutoField name='locationDescription' />
              <AutoField name='calibration_constant'/>
              <AutoField name='threshold_percent_f_low'/>
              <AutoField name='threshold_percent_f_high'/>
              <AutoField name='threshold_percent_v_low'/>
              <AutoField name='threshold_percent_v_high'/>
              <AutoField name='threshold_percent_thd_high'/>
              <AutoField name='owners' />
              <SubmitField value='Submit'/>
              <ErrorsField/>
            </Segment>
          </AutoForm>
          <Button attached='bottom' size='tiny' as={Link} to={'/admin/manage/opqbox/'}>Back to Manage OPQBoxes</Button>
        </WidgetPanel>
      </Container>
    );
  }
}

/** Uniforms adds 'model' to the props, which we use. */
EditBoxPage.propTypes = {
  ready: PropTypes.bool.isRequired,
  doc: PropTypes.object,
  model: PropTypes.object,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :_id.
  const boxID = match.params.box_id;
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  const userProfilesSubscription = Meteor.subscribe(UserProfiles.getPublicationName());
  const boxOwnersSubscription = Meteor.subscribe(BoxOwners.getPublicationName());
  const makaiConfigSubscription = Meteor.subscribe(MakaiConfig.getPublicationName());

  // if (makaiConfigSubscription.ready() && opqBoxesSubscription.ready()) {
  //   console.log(Object.assign(MakaiConfig.getTriggeringOverrideOrDefault(boxID), OpqBoxes.findBox(boxID)));
  //   // const triggering = MakaiConfig.getTriggeringOverrideOrDefault(boxID);
  // } else {
  //   console.log("Collections aint be ready");
  // }

  const ready = opqBoxesSubscription.ready() && locationsSubscription.ready() &&
      userProfilesSubscription.ready() && boxOwnersSubscription.ready() && makaiConfigSubscription.ready();

  // const doc = ready ? Object.assign(OpqBoxes.findBox(boxID), MakaiConfig.getTriggeringOverrideOrDefault(boxID)) : OpqBoxes.findBox(boxID);

  return {
    ready: ready,
    // doc: doc,
    doc: OpqBoxes.findBox(boxID),
    // doc: Object.assign(OpqBoxes.findBox(boxID), MakaiConfig.getTriggeringOverrideOrDefault(boxID)),
    // doc: { ...OpqBoxes.findBox(boxID), ...MakaiConfig.getTriggeringOverrideOrDefault(boxID) },
  };
})(withRouter(EditBoxPage));
