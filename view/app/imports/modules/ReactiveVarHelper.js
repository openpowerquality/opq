import { Blaze } from 'meteor/blaze';
import { ReactiveVar } from 'meteor/reactive-var';

export class ReactiveVarHelper {
  constructor(templateInstance, reactiveVar = new ReactiveVar()) {
    this.template = templateInstance;
    this.reactiveVar = reactiveVar;
    this.previousValue = null;
    // this.reactiveVar = new ReactiveVar();
    this.onChangeCallbacks = [];
    this.initAutorun();
  }

  initAutorun() {
    // Setup autorun to call onChange callbacks whenever ReactiveVar value changes.
    this.template.autorun(() => {
      const value = this.reactiveVar.get();
      if (value) {
        this.triggerOnChangeCallbacks(value);
      }
    });
  }

  // Registers additional callback.
  onChange(callback) {
    this.onChangeCallbacks.push(callback);
  }

  triggerOnChangeCallbacks(newValue) {
    this.onChangeCallbacks.forEach(cb => cb(newValue));
  }

  /**
   * Get the current value held by the ReactiveVar.
   * @return {*} The current value.
   */
  get() {
    return this.reactiveVar.get();
  }

  /**
   * Set a new value for the ReactiveVar.
   * @param {*} value - The value to set.
   */
  set(value) {
    this.previousValue = this.get();
    this.reactiveVar.set(value);
  }

  getPreviousValue() {
    return this.previousValue;
  }

  static onChangeAny(templateInstance, reactiveVarHelperInstances, callback) {
    if (!(templateInstance instanceof Blaze.TemplateInstance)) {
      throw new Error('ReactiveVarHelper.onChangeAny: Must pass a valid template instance.');
    }
    if (!Array.isArray(reactiveVarHelperInstances)) {
      throw new Error('ReactiveVarHelper.onChangeAny: Must pass a single array of ReactiveVarHelper instances.');
    }
    reactiveVarHelperInstances.forEach(rv => {
      if (!(rv instanceof ReactiveVarHelper)) {
        throw new Error('ReactiveVarHelper.onChangeAny: Array elements must be instances of ReactiveVarHelper');
      }
    });
    if (!(typeof callback === 'function')) {
      throw new Error('ReactiveVarHelper.onChangeAny: Callback must be a function.');
    }

    templateInstance.autorun(() => {
      const rvValues = reactiveVarHelperInstances.map(rv => rv.get());
      // Double bangs handle null/undefined cases.
      const noFalsyValues = rvValues.reduce((accum, current) => !!accum && !!current);
      if (rvValues.length === reactiveVarHelperInstances.length && noFalsyValues) {
        callback(...rvValues);
      }
    });
  }

  static onChangeAll(templateInstance, reactiveVarHelperInstances, callback) {
    if (!(templateInstance instanceof Blaze.TemplateInstance)) {
      throw new Error('ReactiveVarHelper.onChangeAll: Must pass a valid template instance.');
    }
    if (!Array.isArray(reactiveVarHelperInstances)) {
      throw new Error('ReactiveVarHelper.onChangeAll: Must pass a single array of ReactiveVarHelper instances.');
    }
    reactiveVarHelperInstances.forEach(rv => {
      if (!(rv instanceof ReactiveVarHelper)) {
        throw new Error('ReactiveVarHelper.onChangeAll: Array elements must be instances of ReactiveVarHelper');
      }
    });
    if (!(typeof callback === 'function')) {
      throw new Error('ReactiveVarHelper.onChangeAll: Callback must be a function.');
    }

    // Grab initial values. Only call the callback once all of these values have changed.
    let prevValues = reactiveVarHelperInstances.map(rv => rv.get());

    templateInstance.autorun(() => {
      const rvValues = reactiveVarHelperInstances.map(rv => rv.get());
      // Double bangs handle null/undefined cases.
      const noFalsyValues = rvValues.reduce((accum, current) => !!accum && !!current);
      const allValuesChanged = rvValues.reduce((accum, current, index) => {
        const isChanged = current !== prevValues[index];
        return accum && isChanged;
      }, true);

      if (rvValues.length === reactiveVarHelperInstances.length && noFalsyValues && allValuesChanged) {
        prevValues = rvValues; // Set the new values to compare against.
        callback(...rvValues);
      }
    });
  }
}
