// import { BlazeLayout } from 'meteor/kadira:blaze-layout';
import './appLayoutPublic.html';

// Sub-Template Inclusions
import '../header/header.js';

Template.appLayoutPublic.onCreated(function appLayoutPublicOnCreated() {
  const template = this;

  template.leftMenuIsExpanded = false;
  template.rightMenuIsExpanded = false;
});

Template.appLayoutPublic.onRendered(function appLayoutPublicOnRendered() {
  const template = this;

  template.$('#main-body .ui.sidebar')
      .sidebar({
        context: $('#main-body')
      });
});

Template.appLayoutPublic.events({
  'click #left-menu-expand-toggle': function(event) {
    const template = Template.instance();

    if (template.leftMenuIsExpanded) {
      template.$('#left-menu').removeClass('expanded');
      template.$('#main-content').removeClass('left-expanded');
      template.$('#left-menu-expand-toggle i.icon').removeClass('chevron left');
      template.$('#left-menu-expand-toggle i.icon').addClass('chevron right');
    } else {
      template.$('#main-content').addClass('left-expanded');
      template.$('#left-menu').addClass('expanded');
      template.$('#left-menu-expand-toggle i.icon').removeClass('chevron right');
      template.$('#left-menu-expand-toggle i.icon').addClass('chevron left');
    }

    template.leftMenuIsExpanded = !template.leftMenuIsExpanded;
  },
  'click #right-menu-expand-toggle': function(event) {
    const template = Template.instance();

    if (template.rightMenuIsExpanded) {
      template.$('#right-menu').removeClass('expanded');
      template.$('#main-content').removeClass('right-expanded');
      template.$('#right-menu-expand-toggle i.icon').removeClass('chevron right');
      template.$('#right-menu-expand-toggle i.icon').addClass('chevron left');
    } else {
      template.$('#main-content').addClass('right-expanded');
      template.$('#right-menu').addClass('expanded');
      template.$('#right-menu-expand-toggle i.icon').removeClass('chevron left');
      template.$('#right-menu-expand-toggle i.icon').addClass('chevron right');
    }

    template.rightMenuIsExpanded = !template.rightMenuIsExpanded;
  }
});