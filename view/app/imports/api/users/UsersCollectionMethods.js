import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Users } from './UsersCollection';
// import { Persons } from './PersonCollection.js';


export const createUser = new ValidatedMethod({
  name: 'Users.createUser',
  validate: new SimpleSchema({
    firstName: { type: String },
    lastName: { type: String },
    email: { // Accounts-password
      type: String,
      label: 'E-mail *',
      regEx: SimpleSchema.RegEx.Email,
    },
    password: { // Accounts-password
      type: String,
    },
  }).validator({ clean: true }),
  run({ firstName, lastName, email, password }) {
    if (!this.isSimulation) {
      return Users.define({ email, password, first_name: firstName, last_name: lastName });
    }
    return null;
  },
});

