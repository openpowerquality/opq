import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
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
    if (!this.isSimulation) {
      const opqBox = OpqBoxes.findOne({ box_id });
      return (opqBox) ? opqBox.calibration_constant : null;
    }
    return null;
  },
});

export const getBoxIDs = new ValidatedMethod({
  name: 'OpqBoxes.getBoxIDs',
  validate: new SimpleSchema({}).validator({ clean: true }),
  run() {
    if (!this.isSimulation) {
      const opqBoxes = OpqBoxes.find({});
      const boxIDs = opqBoxes.map(box => box.box_id);
      return boxIDs;
    }
    return null;
  },
});
