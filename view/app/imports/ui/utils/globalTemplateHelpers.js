// Global template helpers
import { createFlashAlertMsgObject } from '../components/flashAlert/flashAlert.js';


Template.registerHelper('getTemplateInstance', function() {
  return Template.instance();
});

Template.registerHelper('getTemplateInstanceVariable', function(varName) {
  const templateVar = Template.instance()[varName];
  return templateVar; // Returns the variable reference or undefined if does not exist.
});

Template.registerHelper('formatDate', function(date) {
  return (typeof date === 'number' || date instanceof Date) ? moment(date).format('HH:mm:ss [[]DD MMM YYYY[]]') : null;
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