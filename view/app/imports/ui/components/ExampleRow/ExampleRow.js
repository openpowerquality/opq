import { Trends } from '../../../api/trends/TrendsCollection';
import React from 'react';
import { Table } from  'semantic-ui-react';
import {withTracker} from 'meteor/react-meteor-data';

const trends = Trends.find();

const ExampleRow = () => (
  <Table.Row>
    <Table.Cell>{trends}</Table.Cell>
  </Table.Row>
)

export default withTracker(() => {
  Meteor.subscribe('Trends');

  return {
    trends: trends.find(),
  };
})(App);
