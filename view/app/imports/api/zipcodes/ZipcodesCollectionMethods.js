import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import SimpleSchema from 'simpl-schema';
import { Zipcodes } from './ZipcodesCollection';

export const getZipcodeLatLng = new ValidatedMethod({
  name: 'Zipcodes.getZipcodeLatLng',
  validate: new SimpleSchema({
    zipcode: { type: String },
  }).validator({ clean: true }),
  run({ zipcode }) {
    if (!this.isSimulation) {
      const zipcodeDoc = Zipcodes.findOne({ zipcode });
      if (zipcodeDoc) {
        return zipcodeDoc;
      }
      throw new Meteor.Error('Zipcode not found.');
    }
    return null;
  },
});

