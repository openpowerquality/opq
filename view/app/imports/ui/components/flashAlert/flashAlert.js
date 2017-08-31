import './flashAlert.html';

Template.flashAlert.onCreated(function() {
  const template = this;
  
  // Validate data context.
  template.autorun(() => {
    new SimpleSchema({
      flashAlertReactiveVar: {type: ReactiveVar},
      withMarginTop: {type: Boolean, optional: true}
    }).validate(Template.currentData());
  });

  template.isActive = new ReactiveVar(false);
  template.flashAlert = template.data.flashAlertReactiveVar; // ReactiveVar from parent template. {message, type, expireAtMillis}.

  // Bootstrap alerts by default have margin-bottom: 20px and no margin-top, because alerts usually start displaying at
  // the top of the page. Setting this variable to 'true' will reverse the margins (20px top, 0px bottom). Useful for
  // when alerts are placed below some other existing page element.
  template.withMarginTop = template.data.withMarginTop;

  // Autorun responsible for displaying and hiding alerts when they expire.
  template.autorun(function() {
    const alert = template.flashAlert.get();

    if (alert) {
      const expireFromNowMs = alert.expireAtMillis - Date.now();
      if (expireFromNowMs > 0) {
        template.isActive.set(true); // Un-hides template contents.

        Meteor.setTimeout(function() {
          template.isActive.set(false); // Hide template contents after timeout.
        }, expireFromNowMs);
      }
    }
  })
});

Template.flashAlert.helpers({
  alertType() {
    const template = Template.instance();
    const alertType = template.flashAlert.get().type;
    switch (alertType) {
      case 'success':
        return 'success';
      case 'info':
        return 'info';
      case 'warning':
        return 'warning';
      case 'danger':
        return 'danger';
      default:
        return 'info';
    }
  },
  isActiveAlert() {
    const template = Template.instance();
    return template.isActive.get();
  },
  getMessage() {
    const template = Template.instance();
    const isActive = template.isActive.get();
    const message = template.flashAlert.get().message;
    return (isActive && message) ? message : null;
  },
  withMarginTop() {
    const template = Template.instance();
    return (template.withMarginTop === true) ? "margin-top: 20px; margin-bottom: 0px" : "";
  }
});

export const createFlashAlertMsgObject = (message, type, durationSeconds) => {
  check(message, String);
  check(type, String);
  check(durationSeconds, Number);

  if (durationSeconds > 60) durationSeconds = 60; // Set max time limit of 1 minute.
  const expireAtMillis = Date.now() + (durationSeconds * 1000); // Milliseconds

  return {message, type, expireAtMillis};
};


export const setFlashAlert = (flashAlertMsgObj, flashAlertRV) => {
  check(flashAlertRV, {
    message: String,
    type: String,
    expireAtMillis: Number
  });
  check(flashAlertRV, ReactiveVar);

  flashAlertRV.set(flashAlertObj);

  return flashAlertObj;
};