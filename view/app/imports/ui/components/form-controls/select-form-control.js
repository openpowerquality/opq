import { Template } from 'meteor/templating';
import './select-form-control.html';

Template.Select_Form_Control.onRendered(function () {
  const template = this;
  template.$('select.dropdown').dropdown();
});

Template.Select_Form_Control.helpers({
  isSelected(key, value) {
    return (key === value) ? true : false; // eslint-disable-line no-unneeded-ternary
  },
});
