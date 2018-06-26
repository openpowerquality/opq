import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { Grid, Loader, Header, Segment } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import HiddenField from 'uniforms-semantic/HiddenField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';

class EditBoxPage extends React.Component {

  /** On submit, look up location slug from description, then call generic base.updateMethod. */
  submit(data) {
    const { _id, name, description, calibration_constant, unplugged, locationDescription } = data;
    const location = Locations.findSlugFromDescription(locationDescription);
    const collectionName = OpqBoxes.getCollectionName();
    const updateData = { id: _id, name, description, calibration_constant, unplugged, location };
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
    const formSchema = new SimpleSchema({
      box_id: String,
      name: String,
      description: String,
      unplugged: Boolean,
      calibration_constant: Number,
      locationDescription: { type: String, allowedValues: locationDescriptions, label: 'Location' },
    });
    this.props.doc.locationDescription = Locations.getDoc(this.props.doc.location).description;
    return (
      <Grid container centered>
        <Grid.Column>
          <Header as="h2" textAlign="center">Edit OPQ Box</Header>
          <AutoForm schema={formSchema} onSubmit={this.submit} model={this.props.doc}>
            <Segment>
              <HiddenField name='box_id'/>
              <AutoField name='name'/>
              <AutoField name='description'/>
              <AutoField name='unplugged'/>
              <AutoField name='calibration_constant'/>
              <AutoField name='locationDescription' />
              <SubmitField value='Submit'/>
              <ErrorsField/>
            </Segment>
          </AutoForm>
        </Grid.Column>
      </Grid>
    );
  }
}

/** Uniforms adds 'model' to the props, which we use. */
EditBoxPage.propTypes = {
  doc: PropTypes.object,
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :_id.
  const boxID = match.params.box_id;
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: opqBoxesSubscription.ready() && locationsSubscription.ready(),
    doc: OpqBoxes.findBox(boxID),
  };
})(EditBoxPage);
