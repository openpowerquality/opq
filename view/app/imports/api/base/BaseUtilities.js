import { Meteor } from 'meteor/meteor';
import { OPQ } from '../opq/Opq';

/**
 * Deletes all documents from all OPQ collections.
 * To be used only in testing mode.
 * @memberOf api/base
 * @throws { Meteor.Error } If there is an integrity issue with the DB prior to deletion.
 * @returns true
 */
export function removeAllEntities() {
  if (Meteor.isTest || Meteor.isAppTest) {
    _.forEach(OPQ.collections, collection => collection._collection.remove({}));
  } else {
    throw new Meteor.Error('removeAllEntities not called in testing mode.');
  }
  return true;
}
