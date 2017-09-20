import { Meteor } from 'meteor/meteor';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { Template } from 'meteor/templating';
import Moment from 'moment';

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
          } else {
            // Otherwise we have the 'normal' case where we can simply validate against the ReactiveVar's value.
            currentSchema.validate(reactiveValue);
          }

          // console.log(`${schemaKey} schema validated`);
        });
      }
    }
  });
};

/**
 * Given a template instance or view, finds and returns the top-most/root template instance by traversing up
 * the view tree.
 * @param {(Blaze.TemplateInstance|Blaze.View)} templateOrView - The TemplateInstance or Blaze View to find the root template of.
 * @returns {Blaze.TemplateInstance} - The root template instance.
 */
export const getRootTemplateInstance = (templateOrView) => {
  let currentView = null;
  if (templateOrView instanceof Blaze.View) {
    currentView = templateOrView;
  } else if (templateOrView instanceof Blaze.TemplateInstance) {
    currentView = templateOrView.view; // Get its corresponding view
  } else {
    throw new Meteor.Error('Invalid arguments - Must be of type TemplateInstance or View');
  }

  // Find root template
  let topMostView = null;
  while (currentView) {
    // Not all Views we are traversing will have a template associated with it - the ones that do have a template
    // property associated with it.
    if (currentView.template) topMostView = currentView;
    currentView = currentView.parentView;
  }

  return topMostView.templateInstance();
};

/**
 * Calculates the appropriate color representation of a numeric value. Evaluated on a linear scale.
 * @param {Number} dataValue - The value to evaluate a color for.
 * @param {Number} minValue - The minimum value to be represented with the first color in the colorRange array.
 * @param {Number} maxValue - The maximum value to be represented with the last color in the colorRange array.
 * @param {String[]} colorRange - An array of hex colors, ordered from least to greatest intended color value.
 * @returns {String} - The calculated hex color representation of the given value.
 */
export const colorQuantify = (dataValue, minValue, maxValue, colorRange) => {
  check(dataValue, Number);
  check(minValue, Number);
  check(maxValue, Number);
  check(colorRange, [String]);

  // DomainDifference / NumColors
  // Gives us the value that evenly splits up the dataDomain based on the given number of colors.
  const dataDomainIncrement = Math.abs(maxValue - minValue) / colorRange.length;

  let resultColor = null;
  for (let i = 0; i < colorRange.length; i++) {
    if (dataValue < minValue + (dataDomainIncrement * (i+1))) {
      resultColor = colorRange[i];
      break;
    }
  }

  // Takes care of case where dataValue is larger than maxValue (chooses the last color). Note that the above loop
  // will take care of the case where dataValue is smaller than minValue (chooses the first color)
  if (!resultColor) resultColor = colorRange[colorRange.length-1];

  return resultColor;
};

/**
 * Returns a unique string representation of the given date 'rounded' to the desired unit of time.
 * @param {Date} date - The date object to evaluate.
 * @param timeUnit - The unit of time to round to. Allowed values: 'year', 'month', 'week', 'day', 'dayOfMonth', 'hourOfDay'
 * @returns {String} - The appropriate string value of the given Date, based on the given unit of time.
 */
export const timeUnitString = (date, timeUnit) => {
  const mDate = Moment(date);
  const hour = mDate.hour(); // 0-23
  const dayOfMonth = mDate.date(); // 1-31
  const day = mDate.dayOfYear(); // 1-366
  const week = mDate.week(); // 1-52
  const month = mDate.month(); // 0-11
  const year = mDate.year(); // 4 digit year

  // All keys are appended with year to ensure uniqueness of key (in case we're given a long time range).
  let timeUnitKey;
  switch(timeUnit) {
    case 'hourOfDay':
      // Hour of day. Format: hour-day-year. E.g. 23-365-2014, 4-125-1999, etc.
      timeUnitKey = `${hour}-${day}-${year}`;
      break;
    case 'dayOfMonth':
      // Day of month. Format: dayOfMonth-month-year. E.g. 28-11-2008, 31-4-2012, etc.
      timeUnitKey = `${dayOfMonth}-${month}-${year}`;
      break;
    case 'day':
      // Day of year. Format: dayOfYear-year. E.g. 365-2002, 147-1945, etc.
      timeUnitKey = `${day}-${year}`;
      break;
    case 'week':
      // Week of year. Format: week-year. E.g. 51-2006, 4-1998, etc.
      timeUnitKey = `${week}-${year}`;
      break;
    case 'month':
      // Month of year. Format: month-year. E.g. 2-1988, 11-2014, etc.
      timeUnitKey = `${month}-${year}`;
      break;
    case 'year':
      // 4 digit year. Format: year. E.g. 1945, 1999, 2017, etc.
      timeUnitKey = year;
      break;
  }

  return timeUnitKey;
};