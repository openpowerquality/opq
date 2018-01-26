import { BlazeLayout } from 'meteor/kadira:blaze-layout';
import './routes';
import '../../ui/utils/globalTemplateHelpers.js';
import '../../ui/stylesheets/site.css';

// Component Templates
import '../../ui/components/form-controls/input-label-block-helper.html';

// Get rid of the default __blaze-root div element and use the regular <body> element instead.
BlazeLayout.setRoot('body');
