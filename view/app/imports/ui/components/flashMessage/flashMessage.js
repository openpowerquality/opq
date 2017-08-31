import { Meteor } from 'meteor/meteor';
import { ReactiveVar } from 'meteor/reactive-var';
import { dataContextValidator } from '../../../utils/utils.js';
import './flashMessage.html';

Template.flashMessage.onCreated(function flashMessageOnCreated() {
  const template = this;

  dataContextValidator(template, new SimpleSchema({
    type: {type: String},
    expireAtMillisFromEpoch: {type: Number, optional: true},
    message: {type: String},
    messageHeader: {type: String, optional: true},
    messageIcon: {type: String, optional: true},
    isDismissible: {type: Boolean, optional: true}
  }), null);


  // FlashMessage references either the given ReactiveVar or a newly created ReactiveVar wrapping the data context.
  template.flashMessage = (Template.currentData().flashMessageReactiveVar) ? Template.currentData().flashMessageReactiveVar : new ReactiveVar();
  // In the case where we wrap the given data context, we update it whenever the data context changes.
  template.autorun(() => {
    const currentData = Template.currentData();
    if (!currentData.flashMessageReactiveVar) {
      template.flashMessage.set(currentData);
    }
  });

  // template.isActive = (Template.currentData().expireAtMillisFromEpoch) ? new ReactiveVar(false) : new ReactiveVar(true);
  template.isActive = (template.flashMessage.get().expireAtMillisFromEpoch) ? new ReactiveVar(false) : new ReactiveVar(true);

  // Hide message when it expires.
  template.autorun(() => {
    const flashMessage = template.flashMessage.get();
    const expireFromNowMs = (flashMessage.expireAtMillisFromEpoch) ? flashMessage.expireAtMillisFromEpoch - Date.now() : 0;
    if (expireFromNowMs > 0 && !template.isActive.get()) {
      template.isActive.set(true);

      Meteor.setTimeout(function() {
        template.isActive.set(false); // Hide template contents after timeout.
      }, expireFromNowMs);
    }
  });

  //
  // // Validate data context.
  // template.autorun(() => {
  //   new SimpleSchema({
  //     flashMessageReactiveVar: {type: ReactiveVar}
  //   }).validate(Template.currentData());
  //
  //   // Must separately validate the ReactiveVar fields.
  //   const flashMessage = Template.currentData().flashMessageReactiveVar.get();
  //   if (flashMessage) { // Only want to validate if the RV holds an actual value.
  //     new SimpleSchema({
  //       type: {type: String},
  //       expireAtMillisFromEpoch: {type: Number, optional: true},
  //       message: {type: String},
  //       messageHeader: {type: String, optional: true},
  //       messageIcon: {type: String, optional: true}
  //     }).validate(flashMessage);
  //   }
  // });
  //
  // template.flashMessage = template.data.flashMessageReactiveVar;
  // template.isActive = new ReactiveVar(false);
  //
  // // Autorun responsible for showing and hiding message when it expires.
  // template.autorun(function() {
  //   const flashMessage = template.flashMessage.get();
  //
  //   if (flashMessage) {
  //     const expireFromNowMs = flashMessage.expireAtMillisFromEpoch - Date.now();
  //     if (expireFromNowMs > 0) {
  //       template.isActive.set(true); // Un-hides template contents.
  //
  //       Meteor.setTimeout(function() {
  //         template.isActive.set(false); // Hide template contents after timeout.
  //       }, expireFromNowMs);
  //     }
  //   }
  // })
});

Template.flashMessage.onRendered(function flashMessageOnRendered() {
  const template = this;

  // Enables functionality for message block to be dismissible. However, the button/icon itself will be visible only
  // if the 'isDismissible' boolean field is set to true on the flashMessage object - which by default is an optional
  // field and therefore false.
  template.$('.message .close')
    .on('click', function() {
      $(this)
        .closest('.message')
        .transition('fade')
      ;
    });
});

Template.flashMessage.helpers({
  messageType() {
    const template = Template.instance();

    const messageType = template.flashMessage.get().type;
    // const messageType = template.flashMessage.type;
    switch (messageType) {
      case 'success': // Green
      case 'positive':
        return 'success';
      case 'error': // Red
      case 'negative':
        return 'error';
      case 'warning': // Yellow
        return 'warning';
      case 'info': // Blue
        return 'info';
      default:
        return 'info';
    }
  },
  hidden() {
    const template = Template.instance();
    const isActive = template.isActive.get();

    // No need to use 'visible' class because div should be visible by default. Would also interfere with Semantic-UI's
    // hidden/visible error form behavior.
    return (!isActive) ? 'hidden' : '';
  },
  message() {
    const template = Template.instance();
    const message = template.flashMessage.get().message;
    // const message = template.flashMessage.message;
    return (message) ? message : '';
  },
  messageHeader() {
    const template = Template.instance();
    const messageHeader = template.flashMessage.get().messageHeader;
    // const messageHeader = template.flashMessage.messageHeader;
    return (messageHeader) ? messageHeader : '';
  },
  hasIcon() {
    const template = Template.instance();
    const messageIcon = template.flashMessage.get().messageIcon;
    // const messageIcon = template.flashMessage.messageIcon;
    return (messageIcon) ? true : false;
  },
  iconName() {
    const template = Template.instance();
    const messageIcon = template.flashMessage.get().messageIcon;
    // const messageIcon = template.flashMessage.messageIcon;
    return (messageIcon) ? messageIcon : '';
  },
  isDismissible() {
    const template = Template.instance();
    const isDismissible = template.flashMessage.get().isDismissible;
    return (isDismissible) ? true : false;
  }
});

export const createFlashMessageMsgObject = (type, durationSeconds, message, messageHeader = '', messageIcon = '') => {
  check(type, String);
  check(durationSeconds, Number);
  check(message, String);
  check(messageHeader, String);
  check(messageIcon, String);

  if (durationSeconds > 60) durationSeconds = 60; // Set max time limit of 1 minute.
  const expireAtMillisFromEpoch = Date.now() + (durationSeconds * 1000); // Milliseconds

  return {type, expireAtMillisFromEpoch, message, messageHeader, messageIcon};
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

export const flashMessageConstructor = (templateInstance) => {
  templateInstance.flashMessage = new ReactiveVar(createFlashMessageMsgObject('negative', 20, 'testing 123', 'Hi!!', 'feed'));
};