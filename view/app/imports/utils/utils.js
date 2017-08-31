import { Meteor } from 'meteor/meteor';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Template } from 'meteor/templating';

/**
 * Experimental function utilizing a Promise object that will eventually return a jQuery object matching the requested
 * selector. Particularly useful in reactive contexts because we don't have to worry about the flush cycle and whether
 * or not the page element has rendered/re-rendered.
 * @param selector - The dom element to select
 * @param intervalMs - The number of milliseconds to wait between each selection attempt.
 * @param timeoutMs - The total number of milliseconds to wait before timing out.
 * @param templateInstance - The template instance from which to select an element.
 * @returns {Promise} - A Promise of a jQuery object matching the given selector.
 */
export const jQueryPromise = (selector, intervalMs, timeoutMs, templateInstance) => {
  return new Promise(function(resolve, reject) {
    timeoutMs = (timeoutMs > 60000) ? 60000 : timeoutMs; // 60 second max timeout.
    const totalRuns = timeoutMs / intervalMs;
    let currentRun = 0;
    let jQueryElement;
    let timer = Meteor.setInterval(() => {
      if (currentRun < totalRuns) {
        currentRun++; // Should be placed up top in case function has runtime error, otherwise infinite loop will occur.

        if (!templateInstance.view.isCreated) {
          reject('Template does not exist.');
          Meteor.clearInterval(timer);
        }
        if (templateInstance.view.isDestroyed) {
          reject('Template has been destroyed and no longer exists.');
          Meteor.clearInterval(timer);
        }

        // Still need to check if template has been destroyed because JS functions always run to completion unless error thrown.
        jQueryElement = (!templateInstance.view.isDestroyed) ? templateInstance.$(selector) : null;
        if (!!jQueryElement) {
          resolve(jQueryElement);
          Meteor.clearInterval(timer);
        }
      }
      else {
        reject(`Unable to select: ${selector}`);
        Meteor.clearInterval(timer);
      }
    }, intervalMs);
  });
};

/**
 * Reactively validates the template's data context. In addition, can validate the contents of any nested ReactiveVars
 * if their schemas are given.
 * @param {Object} templateInstance - The template instance.
 * @param {SimpleSchema} baseSchema - The SimpleSchema of the base data context object.
 * @param {Object} nestedReactiveVarSchemas - The SimpleSchemas of all ReactiveVars that need to be validated.
 */
export const dataContextValidator = (templateInstance, baseSchema, nestedReactiveVarSchemas) => {
  // check(templateInstance, Object);
  check(baseSchema, SimpleSchema);

  // Validate data context. If it is an RV-wrapped data context, retrieve it first.
  templateInstance.autorun(() => {
    // const dataContext = templateInstance.currentData(); // Trigger computation whenever data context changes.
    const dataContext = Template.currentData();

    if (dataContext) {
      // Validate against base schema.
      baseSchema.validate(dataContext);
      console.log('BaseSchema validated');

      /**
       * Validate all given ReactiveVar schemas with their respective data context objects. ReactiveVar values are
       * retrieved before being validated against.
       */
      if (nestedReactiveVarSchemas) {
        Object.keys(nestedReactiveVarSchemas).forEach((schemaKey) => {
          const currentSchema = nestedReactiveVarSchemas[schemaKey];

          // Ensure that the corresponding data context key actually references a ReactiveVar, before we call get() on it.
          if (!(dataContext[schemaKey] instanceof ReactiveVar)) {
            throw new Meteor.Error('not-reactive-var', 'The reactive var schema key name was not found in the given ' +
                'data context object.');
          }

          // Get the ReactiveVar's value and validate against its respective schema.
          const reactiveValue = dataContext[schemaKey].get();

          /**
           * Handle ReactiveVars that only hold a single primitive value.
           * In these cases, the given schema definition should not be an actual SimpleSchema object, but rather just
           * the individual schema rules object eg. {type: String, label: 'First Name'}.
           */
          if (!(currentSchema instanceof SimpleSchema) && typeof currentSchema === 'object') {
            /**
             * Have to create a temporary schema and object to validate against since SimpleSchema expects to validate
             * against an object with key, val pairs.
             */
            new SimpleSchema({
              _singleKeySchema: currentSchema // currentSchema, in this case, just holds the schema rules object. See above.
            }).validate({_singleKeySchema: reactiveValue});
            console.log('single validation');
          } else {
            // Otherwise we have the 'normal' case where we can simply validate against the ReactiveVar's value.
            currentSchema.validate(reactiveValue);
            console.log('regular validation');
          }

          console.log(`${schemaKey} schema validated`);
        });
      }
    }
  });
};
