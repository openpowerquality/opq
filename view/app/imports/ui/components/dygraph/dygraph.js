import { Template } from 'meteor/templating';
import { dataContextValidator } from '../../../utils/utils.js';
import Dygraph from 'dygraphs';
import '../../../../node_modules/dygraphs/dist/dygraph.css';
import './dygraph.html';

Template.dygraph.onCreated(function() {
  const template = this;

  // Validation is very slow for large array dataset. Skip validation until simple-schema bug fixed.
  // dataContextValidator(template, new SimpleSchema({
  //   dygraphData: {type: [[Number]], decimal: true},
  //   dygraphOptions: {type: Object, optional: true, blackbox: true},
  //   dygraphSync: {type: Function, optional: true}
  // }), null);

});

Template.dygraph.onRendered(function() {
  const template = this;

  // Create Chart
  // template.autorun(() => {
    // const data = Template.currentData().dygraphData;
    const data = template.data.dygraphData;
    // const options = Template.currentData().dygraphOptions;
    const options = template.data.dygraphOptions;
    // const sync = Template.currentData().dygraphSync;
    const sync = template.data.dygraphSync;

    if (data) {
      // Get div - Dygraphs requires the raw DOM element.
      const ctx = template.$('.dygraph-div').get(0);

      // Instantiate the graph
      template.graph = new Dygraph(ctx, data, options);

      // Sync Graph
      if (sync) sync(template.graph);
    }
  // });

});