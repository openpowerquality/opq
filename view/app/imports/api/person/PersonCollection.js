import BaseCollection from '../base/BaseCollection.js';

class PersonCollection extends BaseCollection {
  constructor() {
    super('Person',
        null,
        new SimpleSchema({
          userId: { // Reference to Users. (From Meteor's Accounts-Password package.)
            type: String,
            regEx: SimpleSchema.RegEx.Id // Meteor's string ID, not Mongo's ObjectID.
          },
          firstName: {
            type: String
          },
          lastName: {
            type: String
          }
        }),
        null
    );

    this.publicationNames = {

    }
  }

  define({userId, firstName, lastName}) {
    const personId = this._collection.insert({userId, firstName, lastName});
    return personId;
  }

  publish() {

  }

}

/**
 * Provides the singleton instance of this class.
 * @type {PersonCollection}
 */
export const Persons = new PersonCollection();