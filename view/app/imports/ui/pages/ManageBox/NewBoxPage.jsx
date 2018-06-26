import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { Bert } from 'meteor/themeteorchef:bert';
import { Grid, Loader, Header, Segment } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { defineMethod } from '/imports/api/base/BaseCollection.methods';

class NewBoxPage extends React.Component {

  /** TODO: On submit, look up location slug from description, then call generic base.defineMethod. */
  submit(data) {
    const { box_id, name, description, calibration_constant, unplugged, locationDescription } = data;
    const location = Locations.findSlugFromDescription(locationDescription);
    const collectionName = OpqBoxes.getCollectionName();
    const definitionData = { box_id, name, description, calibration_constant, unplugged, location };
    defineMethod.call({ collectionName, definitionData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Definition failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Definition succeeded' })));
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form. Convert location slugs (from doc) into descriptions for display.
   * TODO: Support defining the list of owners.
   */
  renderPage() {
    const locationDescriptions = Locations.getDocs().map(doc => doc.description);
    locationDescriptions.unshift('Select a location');
    const formSchema = new SimpleSchema({
      box_id: String,
      name: String,
      description: String,
      unplugged: { type: Boolean, defaultValue: false },
      calibration_constant: Number,
      locationDescription: { type: String, allowedValues: locationDescriptions, label: 'Location' },
    });
    return (
      <Grid container centered>
        <Grid.Column>
          <Header as="h2" textAlign="center">New OPQ Box</Header>
          <AutoForm schema={formSchema} onSubmit={this.submit}>
            <Segment>
              <AutoField name='box_id'/>
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
NewBoxPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: opqBoxesSubscription.ready() && locationsSubscription.ready(),
  };
})(NewBoxPage);
