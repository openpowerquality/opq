import React from 'react';
import { Grid, Loader, Header, Segment, Form } from 'semantic-ui-react';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { editBox } from '/imports/api/opq-boxes/OpqBoxesCollectionMethods';
import { Bert } from 'meteor/themeteorchef:bert';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import { _ } from 'lodash';

/** Renders the Page for editing a single document. */
class EditBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      box_id: props.doc.box_id,
      name: props.doc.name,
      description: props.doc.description,
      calibration_constant: props.doc.calibration_constant,
      location: props.doc.location,
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

   handleChange(e, { name, value }) {
    this.setState({ [name]: value });
  }

   handleSubmit() {
    const { box_id, name, description, calibration_constant, location } = this.state;
    editBox.call({ box_id, name, description, calibration_constant, location }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** Form using Uniforms: https://github.com/vazco/uniforms */
  renderPage() {
    const currentLocation = Locations.findLocation(this.props.doc.location).description;
    const locations = Locations.getLocations();
    const options = _.map(locations, loc => {
      return {
        text: Locations.findLocation(loc).description,
        value: Locations.findLocation(loc).slug,
      };
    });

    return (
        <Grid container centered>
          <Grid.Column>
            <Header as="h2" textAlign="center">Edit Box</Header>
            <Form onSubmit={this.handleSubmit}>
              <Segment>
                <Form.Field>
                  <label>Name</label>
                  <Form.Input defaultValue={this.props.doc.name} name="name" onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Description</label>
                  <Form.Input placeholder='Enter additional box information...'
                              defaultValue={this.props.doc.description}
                              onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Calibration Constant</label>
                  <Form.Input name="calibration_constant" placeholder='Enter value...' type='number'
                              defaultValue={this.props.doc.calibration_constant}
                              onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Current location</label>
                  <Form.Select name="location" options={options} placeholder={currentLocation}
                               onChange={this.handleChange}/>
                </Form.Field>
                <Form.Button content="Submit"/>
              </Segment>
            </Form>
          </Grid.Column>
        </Grid>
    );
  }
}

/** Uniforms adds 'model' to the props */
EditBox
    .propTypes = {
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
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    doc: OpqBoxes.findBox(documentId),
    ready: opqBoxesSubscription.ready() && locationsSubscription.ready(),
  };
})(EditBox);
