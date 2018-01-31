import React from 'react';
import { Table } from 'semantic-ui-react';

import ExampleRow from '../ExampleRow/ExampleRow';

// const Rows = (num) => {
//   rows = [];
//   for(let i = 0; i < num; i++)
//   rows.append(<ExampleRow />);
// }

const ExampleTable = () => (
  <Table celled striped>
    <Table.Header>
      <Table.Row textAlign='center'>
        <Table.HeaderCell>Trends average THD values</Table.HeaderCell>
      </Table.Row>
      <ExampleRow/>
    </Table.Header>

  </Table>
)

export default ExampleTable
