// Global template helpers
import { createFlashAlertMsgObject } from '../components/flashAlert/flashAlert.js';
import { getRootTemplateInstance } from '../../utils/utils.js';
import Moment from 'moment';


Template.registerHelper('getTemplateInstance', function() {
  return Template.instance();
});

Template.registerHelper('getTemplateInstanceVariable', function(varName) {
  const templateVar = Template.instance()[varName];
  return templateVar; // Returns the variable reference or undefined if does not exist.
});

Template.registerHelper('formatDate', function(date) {
  return (typeof date === 'number' || date instanceof Date) ? Moment(date).format('HH:mm:ss [[]DD MMM YYYY[]]') : null;
});

Template.registerHelper('formatDateMDY', function(date) {
  let dateString;
  if (typeof date === 'number' || date instanceof Date) dateString = Moment(date).format('MMM D, YYYY');
  if (date === 'today') dateString = Moment().format('MMM D, YYYY');
  return dateString;
});

Template.registerHelper('formatDecimals', function(decimals, number) {
  return (typeof number === 'number' && typeof decimals === 'number') ? number.toFixed(decimals) : null;
});

Template.registerHelper('showFlashAlert', function(templateInstance) {
  const message = templateInstance.flashAlert.get();
  if (message) {
    return message;
  }
  return (message) ? message : null;
});

export const setFlashAlert = (message, templateInstance) => {
  check(message, String);
  templateInstance.flashAlert = new ReactiveVar(message);
};

Template.registerHelper('consoleLog', function(obj) {
  console.log(obj);
});

Template.registerHelper('flashAlertMsgObj', createFlashAlertMsgObject);

/**
 * Call this helper whenever we create a template inclusion that does not require any data context.
 *
 * Reasoning: Template inclusions that do not have any arguments will automatically inherit the data context of the
 * template where it was called from. Often, the inherited data is not needed at all by the sub-template, in which
 * case it is pointless to include it, as it just adds another layer of confusion.
 * The reason we use an empty object rather than an empty string (which is what the official Blaze docs shows as an
 * example) is because in an object is required for the template-level data context validation that we perform on
 * our templates.
 */
Template.registerHelper('withEmptyDataContext', () => {
  return {};
});

Template.registerHelper('generateRandomIdString', () => {
  return Random.id();
});

Template.registerHelper('isEqual', (first, second) => {
  return first === second;
});

Template.registerHelper('fieldError', (fieldName) => {
  const validationContext = Template.instance().validationContext;
  const invalidKeys = validationContext.invalidKeys();
  // console.log('Validation context invalidKeys', invalidKeys);
  const errorObj = _.find(invalidKeys, (keyErrorObj) => keyErrorObj.name === fieldName);
  // if (errorObj) console.log(validationContext.keyErrorMessage(errorObj.name));
  return (errorObj) ? validationContext.keyErrorMessage(errorObj.name) : '';
});

Template.registerHelper('hasFormError', () => {
  const validationContext = Template.instance().validationContext;
  return !validationContext.isValid();
});

Template.registerHelper('formSubmissionErrors', () => {
  // Assumes there is a ReactiveVar on the template named formSubmissionErrors.
  const formSubmissionErrors = Template.instance().formSubmissionErrors.get();
  return formSubmissionErrors;
});

Template.registerHelper('dataSource', (uniqIdentifier) => {
  const template = Template.instance();

  // DataSources is an object mapping UIDs to their ReactiveVars.
  // Each template can have a variable named 'dataSources' which keeps track of all RV sources attached to the current
  // template. Subsequently, the dataSink() helper will be able to lookup data sources and retrieve their current data.
  if (template.dataSources) {
    // Create ReactiveVar for the UID if it does not yet exist. If it does already exist, we don't need to do
    // anything; it will be returned at the end of function.
    if (!template.dataSources[uniqIdentifier]) template.dataSources[uniqIdentifier] = new ReactiveVar();
  } else {
    // DataSources obj does not exist yet for this template, so create it.
    template.dataSources = {[uniqIdentifier]: new ReactiveVar()}
  }

  return template.dataSources[uniqIdentifier]; // Return the ReactiveVar reference (not value!)
});

Template.registerHelper('dataSink', (uniqIdentifier) => {
  // We want this dataSink() helper to be able to access dataSources defined not only in the same template, but
  // also across other templates and files. To accomplish this, we will search through every currently rendered
  // template's dataSources object for the given source identifier using the Template.forEachCurrentlyRenderedInstance()
  // function from the aldeed:template-extension package.
  // However, since these global helpers are parsed before templates are actually rendered, we need a way to wait until
  // all templates have been rendered. As a result, we've created and attached an _isRendered ReactiveVar to each
  // template (see /imports/startup/client/index.js), which is set to true once the template is rendered. This is
  // useful in itself because we now have a way to reactively detect when a template has been rendered. However, to
  // know when ALL templates have been rendered, we can simply check if the top-most template has been rendered,
  // because Blaze loads children templates first and works its way up the view tree. Once the top-most template has
  // been rendered, we can go ahead and iterate through all rendered templates to search for the appropriate dataSource.

  // Search each currently rendered template's dataSources object for the given source identifier.
  // The top-most template is the last template to render, so once it's loaded, we know all templates are loaded.
  const isAllTemplatesRendered = getRootTemplateInstance(Template.instance())._isRendered.get();

  if (isAllTemplatesRendered) {
    let sourceTemplate = null;
    Template.forEachCurrentlyRenderedInstance(template => {
      // console.log(template);
      if (template.dataSources && template.dataSources[uniqIdentifier]) sourceTemplate = template;
    });

    if (sourceTemplate) {
      return sourceTemplate.dataSources[uniqIdentifier].get();
    } else {
      // Should throw error, since there should never be a sink without a source.
      throw new Error(`${uniqIdentifier} dataSource not found.`);
    }
  }

  // Initially return null. Templates have not yet finished loading at this point.
  return null;
});

Template.registerHelper('getRoutePath', (routeName) => {
  return FlowRouter.path(routeName);
});

/**
 * Given a set of key-val pairs, will return an object with those key-val pairs.
 * Usage: {{> someTemplate someParam=(object key1="value1" key2="value2")}}
 * See http://blazejs.org/guide/spacebars.html#Calling-helpers-with-arguments on how this works.
 */
Template.registerHelper('object', ({ hash }) => {
  return hash;
});