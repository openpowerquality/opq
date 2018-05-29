import { Meteor } from 'meteor/meteor';
import { DDP } from 'meteor/ddp-client';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import { OPQ } from '../opq/Opq';
import { removeAllEntities } from '../base/BaseUtilities';

/* global Assets */

/** Whether or not to print out a line indicating how many objects were defined in each collection. */
const consolep = false;

/**
 * Returns the definition array associated with collectionName in the loadJSON structure,
 * or an empty array if none was found.
 * @param loadJSON The load file contents.
 * @param collection The collection of interest.
 * @memberOf api/test
 */
function getDefinitions(loadJSON, collection) {
  const definitionObj = _.find(loadJSON.collections, obj => obj.name === collection);
  return definitionObj ? definitionObj.contents : [];
}

/**
 * Given a collection and the loadJSON structure, looks up the definitions and invokes define() on them.
 * @param collection The collection to be loadd.
 * @param loadJSON The structure containing all of the definitions.
 * @param consolep output console.log message if truey.
 * @memberOf api/test
 */
export function loadCollection(collection, loadJSON) {
  const definitions = getDefinitions(loadJSON, collection._collectionName);
  if (consolep && definitions.length) {
    console.log(`Defining ${definitions.length} ${collection._collectionName} documents.`); // eslint-disable-line
  }
  _.each(definitions, definition => collection.define(definition));
}

/**
 * Loads data from a modular test fixture file.
 * @param fixtureName The name of the test fixture data file. (located in private/database/fixture).
 * @memberOf api/test
 */
export function defineTestFixture(fixtureName) {
  if (Meteor.isServer) {
    const loadFileName = `database/fixture/${fixtureName}`;
    const loadJSON = JSON.parse(Assets.getText(loadFileName));
    console.log(`    Loaded ${fixtureName} (${loadJSON.fixtureDescription})`);
    _.each(OPQ.collectionLoadSequence, collection => loadCollection(collection, loadJSON));
  }
}

/**
 * Loads all the data from an array of fixture file names.
 * @param fixtureNames an array of the name of the test fixture data file. (located in private/database/modular).
 * @memberOf api/test
 */
export function defineTestFixtures(fixtureNames) {
  _.each(fixtureNames, fixtureName => defineTestFixture(`${fixtureName}.fixture.json`));
}

/**
 * A validated method that loads the passed list of fixture files in the order passed.
 * @memberOf api/test
 */
export const defineTestFixturesMethod = new ValidatedMethod({
  name: 'test.defineTestFixturesMethod',
  mixins: [CallPromiseMixin],
  validate: null,
  run(fixtureNames) {
    removeAllEntities();
    defineTestFixtures(fixtureNames);
    return true;
  },
});

/**
 * Returns a Promise that resolves when all RadGrad collections subscriptions are ready.
 * @see {@link https://guide.meteor.com/testing.html#full-app-integration-test}
 * @memberOf api/test
 */
export function withOpqSubscriptions() {
  return new Promise(resolve => {
    _.each(OPQ.collections, collection => collection.subscribe());
    const poll = Meteor.setInterval(() => {
      if (DDP._allSubscriptionsReady()) {
        Meteor.clearInterval(poll);
        resolve();
      }
    }, 200);
  });
}

export const testUsername = 'opqtestuser@hawaii.edu';
export const testUserPassword = 'foo';

/**
 * Returns a Promise that resolves if one can successfully login with the passed credentials.
 * Credentials default to the standard admin username and password.
 * @memberOf api/test
 */
export function withLoggedInUser({ username = testUsername, password = testUserPassword } = {}) {
  return new Promise((resolve, reject) => {
    Meteor.loginWithPassword(username, password, (error) => {
      if (error) {
        console.log('Error: withLoggedInUser', error);
        reject();
      } else {
        resolve();
      }
    });
  });
}

