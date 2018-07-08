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
import { Locations } from '/imports/api/locations/LocationsCollection';
import { UserProfiles } from '/imports/api/users/UserProfilesCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { updateMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';

class EditLocationPage extends React.component {

  helpText = `
  <p>Edit an OPQ location.</p>
  <p>Click 'Back to Manage Locations' to return to the listing page.</p>
  `;


  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** On submit, look up location slug from description, then call generic base.updateMethod. */
  submit(data) {
    const { slug, coordinates, description } = data;
    const collectionName = Locations.getCollectionName();
    const updateData = { slug: slug, coordinates, description };
    updateMethod.call({ collectionName, updateData }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  /**
   * Render the form. Use Uniforms: https://github.com/vazco/uniforms.
   * Create a custom schema for the form. Convert location slugs (from doc) into descriptions for display.
   */
  renderPage() {
    const formSchema = new SimpleSchema({
      slug: String,
      coordinates: { type: Array },
      'coordinates.$': { type: Number },
      description: String,
    });
    // Update the Uniforms model with current values for locationDescription and Owners.
    this.props.doc.locationDescription = Locations.getDoc(this.props.doc.location).description;
    return (
        <Container>
          <WidgetPanel title="Edit Location" helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit} model={this.props.doc}>
              <Segment>
                <HiddenField name='slug'/>
                <AutoField name='coordinates'/>
                <AutoField name='description'/>
                <SubmitField value='Submit'/>
                <ErrorsField/>
              </Segment>
            </AutoForm>
            <Button attached='bottom' size='tiny'>
              <Link to={'/admin/manage/location/'}>Back to Manage Locations</Link>
            </Button>
          </WidgetPanel>
        </Container>
    );
  }
}

/** Uniforms adds 'model' to the props, which we use. */
EditLocationPage.propTypes = {
  doc: PropTypes.object,
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :slug.
  const slug_param = match.params.slug;
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: locationsSubscription.ready(),
    doc: Locations.getDoc(slug_param),
  };
})(withRouter(EditLocationPage));

