import React from 'react';
import { Grid, Loader, Header, Segment } from 'semantic-ui-react';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { editBox } from '/imports/api/opq-boxes/OpqBoxesCollectionMethods';
import AutoForm from 'uniforms-semantic/AutoForm';
import TextField from 'uniforms-semantic/TextField';
import SubmitField from 'uniforms-semantic/SubmitField';
import ErrorsField from 'uniforms-semantic/ErrorsField';
import NumField from 'uniforms-semantic/NumField';
import { Bert } from 'meteor/themeteorchef:bert';
import ListField from 'uniforms-semantic/ListField';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';

/** Renders the Page for editing a single document. */
class EditBox extends React.Component {

  /** On successful submit, call editBox method to insert data. */
  submit(data) {
    const { box_id, name, description, calibration_constant, locations } = data;
    editBox.call({ box_id, name, description, calibration_constant, locations }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  /** If the subscription(s) have been received, render the page, otherwise show a loading icon. */
  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** Form using Uniforms: https://github.com/vazco/uniforms */
  renderPage() {
    return (
        <Grid container centered>
          <Grid.Column>
            <Header as="h2" textAlign="center">Edit Box</Header>
            <AutoForm schema={OpqBoxes.getSchema()} onSubmit={this.submit} model={this.props.doc}>
              <Segment>
                <TextField name='name'/>
                <TextField name='description'/>
                <NumField name='calibration_constant'/>
                <ListField name='locations'/>
                <SubmitField value='Submit'/>
                <ErrorsField/>
              </Segment>
            </AutoForm>
          </Grid.Column>
        </Grid>
    );
  }
}

/** Uniforms adds 'model' to the props */
EditBox.propTypes = {
  doc: PropTypes.object,
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :_id.
  const documentId = match.params.box_id;
  // Get access to OpqBoxes documents.
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  return {
    doc: OpqBoxes.findBox(documentId),
    ready: opqBoxesSubscription.ready(),
  };
})(EditBox);
