// import { BlazeLayout } from 'meteor/kadira:blaze-layout';
import './appLayoutAuth.html';

// Sub-Template Inclusions
import '../header/header.js';

Template.appLayoutAuth.onCreated(function() {
  const template = this;

  /**
   * Can be true/false/null. The target template is responsible for setting the authorization result (true/false),
   * typically through the success/failure callback of the template subscription function.
   * A value of null represents an 'unknown' authorization status, which only occurs on initial template creation or
   * when the user logs out.
   */
  template.isAuthorized = new ReactiveVar(null);

  template.autorun(function() {
    const isAuth = template.isAuthorized.get();
    const userId = Meteor.userId();

    if (!userId) template.isAuthorized.set(null); // Reset to null if user logs out.
    console.log('isAuthorized autorun: ', isAuth);
  });

});

Template.appLayoutAuth.helpers({
  canShow() {
    /**
     * A value of null represents an 'unknown' authorization status, which only occurs on initial template creation or
     * when the user logs out. This is necessary in order to allow the canShow() function to display the target
     * template before the authorization has occurred, as the target template is the one responsible for setting the
     * authorization result (true/false) - typically through though the success/failure callback of the template
     * subscription function.
     */
    const template = Template.instance();
    const isAuthorized = template.isAuthorized.get();
    const userId = Meteor.userId();

    return (userId && (isAuthorized || isAuthorized === null)) ? true : false;
  },
  getIsAuthorizedReference() {
    const template = Template.instance();

    // For some reason, Template.dynamic requires us to set the data context through the 'data' variable. As such, if
    // we want to have a named data context variable (isAuthorizedReactiveVar in our case), we have to create the
    // object here.
    return {isAuthorizedReactiveVar: template.isAuthorized};
  }
});