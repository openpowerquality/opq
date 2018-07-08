import { Meteor } from 'meteor/meteor';
import React from 'react';
import PropTypes from 'prop-types';
import { withRouter, Link } from 'react-router-dom';
import { Bert } from 'meteor/themeteorchef:bert';
import { Loader, Segment, Container, Button } from 'semantic-ui-react';
import AutoForm from 'uniforms-semantic/AutoForm';
import AutoField from 'uniforms-semantic/AutoField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { withTracker } from 'meteor/react-meteor-data';
import SimpleSchema from 'simpl-schema';
import { defineMethod } from '/imports/api/base/BaseCollection.methods';
import WidgetPanel from '/imports/ui/layouts/WidgetPanel';

class NewLocationPage extends React.Component {

  helpText = `
  <p>Add a new OPQ Location.</p>
  `;

  /** TODO: On submit, look up location slug from description, then call generic base.defineMethod. */
  submit(data) {
    const { slug, coordinates, description } = data;
    const collectionName = Locations.getCollectionName();
    const definitionData = { slug, coordinates, description };
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
    const formSchema = new SimpleSchema({
      slug: String,
      coordinates: { type: Array },
      'coordinates.$': { type: Number },
      description: String,
    });
    return (
        <Container>
          <WidgetPanel title="Add Location" helpText={this.helpText} noPadding>
            <AutoForm schema={formSchema} onSubmit={this.submit}>
              <Segment>
                <AutoField name='slug'/>
                <AutoField name='coordinates'/>
                <AutoField name='description'/>
                <SubmitField value='Submit'/>
                <ErrorsField/>
              </Segment>
            </AutoForm>
            <Button attached='bottom' size='tiny'>
              <Link to={'/admin/manage/location/'}>Back to Manage OPQBoxes</Link>
            </Button>
          </WidgetPanel>
        </Container>
    );
  }
}

/** Uniforms adds 'model' to the props, which we use. */
NewLocationPage.propTypes = {
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(() => {
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: locationsSubscription.ready(),
  };
})(withRouter(NewLocationPage));
