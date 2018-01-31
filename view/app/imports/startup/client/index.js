import React from 'react';
import { render } from 'react-dom';
import { Meteor } from 'meteor/meteor';
import ExampleLayout from '../../ui/layouts/ExampleLayout/ExampleLayout';
import '../both';

import 'semantic-ui-css/semantic.css';

Meteor.startup(() => render(<ExampleLayout />, document.getElementById('react-root')));
