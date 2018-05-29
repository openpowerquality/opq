import React from 'react';
import { Grid, Loader, Header, Segment, Form } from 'semantic-ui-react';
import { OpqBoxes } from '/imports/api/opq-boxes/OpqBoxesCollection';
import { Locations } from '/imports/api/locations/LocationsCollection';
import { editBox } from '/imports/api/opq-boxes/OpqBoxesCollection.methods';
import { Bert } from 'meteor/themeteorchef:bert';
import { Meteor } from 'meteor/meteor';
import { withTracker } from 'meteor/react-meteor-data';
import PropTypes from 'prop-types';
import { _ } from 'lodash';

/** Renders the Page for editing a single document. */
class EditBox extends React.Component {
  constructor(props) {
    super(props);
    const doc = OpqBoxes.findBox(props.boxID);
    this.state = {
      box_id: doc.box_id,
      name: doc.name,
      description: doc.description,
      calibration_constant: doc.calibration_constant,
      location: doc.location,
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

   handleChange(e, { name, value }) {
    this.setState({ [name]: value });
    console.log('state', this.state);
  }

   handleSubmit() {
    const { box_id, name, description, calibration_constant, location } = this.state;
    console.log('submitting', this.state);
    editBox.call({ box_id, name, description, calibration_constant, location }, (error) => (error ?
        Bert.alert({ type: 'danger', style: 'growl-bottom-left', message: `Update failed: ${error.message}` }) :
        Bert.alert({ type: 'success', style: 'growl-bottom-left', message: 'Update succeeded' })));
  }

  render() {
    return (this.props.ready) ? this.renderPage() : <Loader>Getting data</Loader>;
  }

  /** Form using Uniforms: https://github.com/vazco/uniforms */
  renderPage() {
    const currentLocationDoc = Locations.findLocation(this.state.location);
    const slugs = Locations.getLocations();
    const options = _.map(slugs, function (slug) {
      const text = Locations.findLocation(slug).description;
      const value = slug;
      return (currentLocationDoc.slug === slug) ? { text, value, selected: true } : { text, value };
    });
    return (
        <Grid container centered>
          <Grid.Column>
            <Header as="h2" textAlign="center">Edit Box</Header>
            <Form onSubmit={this.handleSubmit}>
              <Segment>
                <Form.Field>
                  <label>Name</label>
                  <Form.Input defaultValue={this.state.name} name="name" onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Description</label>
                  <Form.Input placeholder='Enter additional box information...'
                              defaultValue={this.state.description}
                              name="description"
                              onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Calibration Constant</label>
                  <Form.Input name="calibration_constant" placeholder='Enter value...' type='number' step='any'
                              defaultValue={this.state.calibration_constant}
                              onChange={this.handleChange}/>
                </Form.Field>
                <Form.Field>
                  <label>Current location</label>
                  <Form.Select name="location" options={options} onChange={this.handleChange}/>
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
EditBox.propTypes = {
  model: PropTypes.object,
  ready: PropTypes.bool.isRequired,
  boxID: PropTypes.string,
};

/** withTracker connects Meteor data to React components. https://guide.meteor.com/react.html#using-withTracker */
export default withTracker(({ match }) => {
  // Get the documentID from the URL field. See imports/ui/layouts/App.jsx for the route containing :_id.
  const boxID = match.params.box_id;
  // Get access to OpqBoxes documents.
  const opqBoxesSubscription = Meteor.subscribe(OpqBoxes.getPublicationName());
  const locationsSubscription = Meteor.subscribe(Locations.getPublicationName());
  return {
    ready: opqBoxesSubscription.ready() && locationsSubscription.ready(),
    boxID,
  };
})(EditBox);
