import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { OpqBoxes } from './OpqBoxesCollection';

export const totalOpqBoxesCount = new ValidatedMethod({
  name: 'OpqBoxes.totalOpqBoxesCount',
  validate: new SimpleSchema().validator({ clean: true }),
  run() {
    return OpqBoxes.find({}).count();
  },
});

export const getBoxCalibrationConstant = new ValidatedMethod({
  name: 'OpqBoxes.getBoxCalibrationConstant',
  validate: new SimpleSchema({
    box_id: { type: String },
  }).validator({ clean: true }),
  run({ box_id }) {
    if (Meteor.isServer) {
      const opqBox = OpqBoxes.findOne({ box_id });
      return (opqBox) ? opqBox.calibration_constant : null;
    }
    return null;
  },
});

export const getBoxesInLoc = new ValidatedMethod({
  name: 'OpqBoxes.getBoxesInLoc',
  validate: new SimpleSchema({
    locations: Array,
    'locations.$': String,
  }).validator({ clean: true }),
  run({ locations }) {
    const boxes = OpqBoxes.find({
      location: { $in: locations },
    });
    const boxIds = boxes.map(box => box.box_id);
    return boxIds;
  },
});

export const getBoxIDs = new ValidatedMethod({
  name: 'OpqBoxes.getBoxIDs',
  validate: new SimpleSchema({}).validator({ clean: true }),
  run() {
    if (Meteor.isServer) {
      const opqBoxes = OpqBoxes.find({});
      const boxIDs = opqBoxes.map(box => box.box_id);
      return boxIDs;
    }
    return null;
  },
});

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
