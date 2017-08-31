import { Template } from 'meteor/templating';
import './radio-field.html';

Template.Radio_Field.onRendered(function () {
  const template = this;
  template.$('.ui.radio.checkbox').checkbox();
});