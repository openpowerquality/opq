import { Template } from 'meteor/templating';
import './checkbox-field.html';

Template.Checkbox_Field.onRendered(function () {
  const template = this;
  template.$('.ui.checkbox').checkbox();
});