/**
 * The Global.Schemas object holds all non-collection definition schemas. Examples of the types of schemas defined here:
 * 1. Entirely non-collection related forms (eg. filter form schema).
 * 2. Schemas that extend an existing collection schema (eg. signup form schema).
 * 3. Schemas that combine multiple existing collection schemas (eg. deviceadmin form schema).
 */

import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import './global.js';
// import { Persons } from '../api/person/PersonCollection.js';
// import '../api/opqDevices/opqDevices.js';
// import '../api/locations/locations.js';

// Register custom validation error messages.
SimpleSchema.messages({
  passwordMismatch: 'Passwords do not match one another',
  incorrectPassword: 'Wrong password - Try again',
  userNotFound: 'User does not exist',
});

/**
 * Filter form schema.
 * @type {SimpleSchema}
 */
Global.Schemas.EventFilters = new SimpleSchema({ // eslint-disable-line no-undef
  requestFreq: {
    type: Boolean,
    optional: true,
    label: ' ', // Due to bug with afFormGroup, must do this to have empty label. Must have space between quotes.
  },
  minFreq: {
    type: Number,
    decimal: true,
  },
  maxFreq: {
    type: Number,
    decimal: true,
  },
  requestVoltage: {
    type: Boolean,
    optional: true,
    label: ' ', // Due to bug with afFormGroup, must do this to have empty label. Must have space between quotes.
  },
  minVoltage: {
    type: Number,
    decimal: true,
  },
  maxVoltage: {
    type: Number,
    decimal: true,
  },
  minDuration: {
    type: Number,
  },
  maxDuration: {
    type: Number,
  },
  itic: {
    type: [Number],
    // allowedValues: [Global.Enums.IticRegion.PROHIBITED, Global.Enums.IticRegion.NO_DAMAGE,
    // Global.Enums.IticRegion.NO_INTERRUPTION],
    // autoform: {
    //   options: [
    //     {label: "Severe", value: Global.Enums.IticRegion.PROHIBITED},
    //     {label: "Moderate", value: Global.Enums.IticRegion.NO_DAMAGE},
    //     {label: "OK", value: Global.Enums.IticRegion.NO_INTERRUPTION}
    //   ]
    // }
  },
  startTime: {
    type: Date,
  },
  stopTime: {
    type: Date,
  },
});

Global.Schemas.MapFilters = new SimpleSchema({ // eslint-disable-line no-undef
  mapCenterLat: {
    type: Number,
    decimal: true,
  },
  mapCenterLng: {
    type: Number,
    decimal: true,
  },
  mapZoom: {
    type: Number,
  },
  mapVisibleIds: {
    type: String,
  },
});

/**
 * Basic login form schema.
 * @type {SimpleSchema}
 */
Global.Schemas.Login = new SimpleSchema({ // eslint-disable-line no-undef
  email: { // Accounts-password
    type: String,
    label: 'E-mail',
    regEx: SimpleSchema.RegEx.Email,
  },
  password: { // Accounts-password
    type: String,
    label: 'Password',
  },
});

/**
 * Form schema for adding a new OPQ box.
 * @type {SimpleSchema}
 */
Global.Schemas.AddOpqBox = new SimpleSchema({ // eslint-disable-line no-undef
  deviceId: {
    type: String,
    label: 'Device ID',
  },
  accessKey: {
    type: String,
    label: 'Access Key',
  },
});

// /**
//  * Signup form schema, extends a portion of the Persons schema. Email and Password fields are manually added,
//  * as there is no defined schema for the Accounts-Password meteor package, for which these fields are required.
//  * @type {SimpleSchema}
//  */
// Global.Schemas.Signup = new SimpleSchema([
//   Persons.getSchema().pick(['firstName', 'lastName', 'alertEmail', 'smsCarrier', 'smsNumber']),
//   {
//     email: { // Accounts-password
//       type: String,
//       label: "E-mail *",
//       regEx: SimpleSchema.RegEx.Email
//     },
//     password: { // Accounts-password
//       type: String,
//       label: "Password *",
//       autoform: { // Need this since using quickForm
//         type: 'password'
//       }
//     },
//     confirmPassword: {
//       type: String,
//       label: "Confirm Password *",
//       autoform: {
//         type: 'password'
//       },
//       custom: function () {
//         if (this.value !== this.field('password').value) {
//           return "passwordMismatch";
//         }
//       }
//     }
//   }
// ]);
//
// export const signupPageSchema = new SimpleSchema([
//   Persons.getSchema().pick(['firstName', 'lastName']),
//   {
//     email: { // Accounts-password
//       type: String,
//       label: "E-mail *",
//       regEx: SimpleSchema.RegEx.Email
//     },
//     password: { // Accounts-password
//       type: String
//     },
//     confirmPassword: {
//       type: String,
//       custom: function () {
//         if (this.value !== this.field('password').value) {
//           return "passwordMismatch";
//         }
//       }
//     }
//   }
// ]);
//
// export const userAdminPageSchema = new SimpleSchema([
//   Persons.getSchema().pick(['userId', 'firstName', 'lastName']),
//   {
//     email: { // Accounts-password
//       type: String,
//       label: "E-mail *",
//       regEx: SimpleSchema.RegEx.Email
//     },
//     password: { // Accounts-password
//       type: String
//     },
//     newPassword: {
//       type: String,
//       optional: true
//     },
//     confirmNewPassword: {
//       type: String,
//       optional: true,
//       custom: function () {
//         if (this.value !== this.field('newPassword').value) {
//           return "passwordMismatch";
//         }
//       }
//     }
//   }
// ]);
//
//
// /**
//  * Schema for "both" forms on the  user settings page (it's actually one form disguised as two).
//  * Extends entire Persons schema with email and password field for Accounts-Password Users collection.
//  * @type {SimpleSchema}
//  */
// Global.Schemas.UserSettings = new SimpleSchema([
//   Persons.getSchema(),
//   {
//   email: { // Accounts-password
//     type: String,
//     label: "E-mail",
//     regEx: SimpleSchema.RegEx.Email
//   },
//   oldPassword: { // Accounts-password
//     type: String,
//     label: "Old Password",
//     optional: true
//   },
//   newPassword: { // Accounts-password
//     type: String,
//     label: "New Password",
//     optional: true
//   },
//   confirmNewPassword: {
//     type: String,
//     label: "Confirm New Password",
//     custom: function () {
//       if (this.value !== this.field('newPassword').value) {
//         return "passwordMismatch";
//       }
//     },
//     optional: true
//   }
// }]);

// Global.Schemas.DeviceadminForm = new SimpleSchema([
//   OpqDevices.simpleSchema().pick(['deviceId', 'accessKey', 'description', 'sharingData']),
//   Locations.simpleSchema(),
//   {
//     device_id: {
//       type: String // Actually ObjectID toString. Must convert to ObjectID on server to utilize.
//     },
//     location_id: {
//       type: String, // ObjectID. See above.
//       optional: true
//     }
//   }
// ]);

export const filterFormSchema = new SimpleSchema({
  minFrequency: { type: Number, optional: true },
  maxFrequency: { type: Number, optional: true },
  minVoltage: { type: Number, optional: true },
  maxVoltage: { type: Number, optional: true },
  minDuration: { type: Number, optional: true },
  maxDuration: { type: Number, optional: true },
  startTime: { type: Number, optional: true },
  endTime: { type: Number, optional: true },
  dayPicker: { type: Number, optional: true },
});
