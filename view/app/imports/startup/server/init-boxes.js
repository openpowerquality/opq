import { Meteor } from 'meteor/meteor';
import { OpqBoxes } from '../../api/opq-boxes/OpqBoxesCollection';


function initBoxes() {
  // Default boxes to an empty array if they are not specified in the settings file.
  const boxes = Meteor.settings.opqBoxes || [];
  console.log(`Initializing ${boxes.length} OPQ boxes.`);
  boxes.map(box => OpqBoxes.define(box));
}

Meteor.startup(() => {
  initBoxes();
});
