import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { OpqBoxes } from './OpqBoxesCollection';

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
