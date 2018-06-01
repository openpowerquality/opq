import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { OpqBoxes } from './OpqBoxesCollection';

export const editBox = new ValidatedMethod({
  name: 'OpqBoxes.editBox',
  validate: new SimpleSchema({
    box_id: String,
    name: { type: String, optional: true },
    description: { type: String, optional: true },
    calibration_constant: { type: Number, optional: true },
    location: { type: String, optional: true },
  }).validator({ clean: true }),
  run({ box_id, name, description, calibration_constant, location }) {
    const loc = OpqBoxes.findOne({ box_id }).location;
    const newLoc = (location === loc) ? loc : location;
    OpqBoxes._collection.update(
        { box_id },
        { $set: { name, description, calibration_constant, location: newLoc } },
    );
  },
});
