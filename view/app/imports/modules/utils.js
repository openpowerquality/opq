import { Meteor } from 'meteor/meteor';
import { check } from 'meteor/check';
import Moment from 'moment';

/**
 * Outputs a progress bar in the console to represent an ongoing operation.
 * Must be updated with updateBar(), and closed with clearInterval(), both of which are returned by this function.
 * @param {Number} total - The number representing the end index of the operation (eg. the collection size)
 * @param {Number} updateRate - The number of milliseconds to wait between each progress bar update.
 * @param {String} message - An informative message placed next to the progress bar.
 * @returns {Object} An object with a clearInterval() and updateBar() functions.
 */
export function progressBarSetup(total, updateRate, message) {
  let timerHandle = null;
  let currentVal = 0;
  const totalVal = total - 1; // Assuming 0 based counting.

  if (!timerHandle) {
    timerHandle = Meteor.setInterval(() => {
      progressBarPrinter(currentVal, totalVal, '=', 30, message); // eslint-disable-line no-use-before-define
    }, updateRate);
  }

  return {
    clearInterval() {
      if (timerHandle) Meteor.clearInterval(timerHandle);
      process.stdout.write('\n'); // Final newline after progressBarPrinter is done.
    },
    updateBar(newCurrent) {
      currentVal = newCurrent;
    },
  };
}

/**
 * Prints the current progress bar state to the console.
 * @param {Number} current - The current position in the operation (eg. the current index position during iteration)
 * @param {Number} total - The end position of the operation (eg. the size of a collection, length of an array).
 * @param {String} tickChar - The character to represent a single tick mark in the progress bar.
 * @param {Number} maxTicks - The total number of ticks the progress bar should have.
 * @param {String} message - An informative message placed next to the progress bar.
 */
export function progressBarPrinter(current, total, tickChar, maxTicks, message) {
  // Create 'empty' progress bar, internally represented as an array. Set start and end brackets of the progress bar.
  const progressBar = Array.from('.'.repeat(maxTicks + 2));
  progressBar[0] = '[';
  progressBar[progressBar.length - 1] = ']';

  const progressPercentage = (current / total) * 100;
  const currentBars = maxTicks * (progressPercentage / 100.0);
  progressBar.fill(tickChar, 1, currentBars + 1);
  // process.stdout.write('\033[F'); // ANSI code to move cursor up one line.
  process.stdout.write('\x1B[F'); // Using hex instead of octal code because of eslint parser error.
  process.stdout.write(`\n\r${message} ${progressBar.join('')} (${progressPercentage.toFixed(1)}%)`);
}

/**
 * Calculates the appropriate color representation of a numeric value. Evaluated on a linear scale.
 * @param {Number} dataValue - The value to evaluate a color for.
 * @param {Number} minValue - The minimum value to be represented with the first color in the colorRange array.
 * @param {Number} maxValue - The maximum value to be represented with the last color in the colorRange array.
 * @param {String[]} colorRange - An array of hex colors, ordered from least to greatest intended color value.
 * @returns {String} - The calculated hex color representation of the given value.
 */
export const colorQuantify = (dataValue, minValue, maxValue, colorRange) => {
  check(dataValue, Number);
  check(minValue, Number);
  check(maxValue, Number);
  check(colorRange, [String]);

  // DomainDifference / NumColors
  // Gives us the value that evenly splits up the dataDomain based on the given number of colors.
  const dataDomainIncrement = Math.abs(maxValue - minValue) / colorRange.length;

  let resultColor = null;
  for (let i = 0; i < colorRange.length; i++) {
    if (dataValue < minValue + (dataDomainIncrement * (i + 1))) {
      resultColor = colorRange[i];
      break;
    }
  }

  // Takes care of case where dataValue is larger than maxValue (chooses the last color). Note that the above loop
  // will take care of the case where dataValue is smaller than minValue (chooses the first color)
  if (!resultColor) resultColor = colorRange[colorRange.length - 1];

  return resultColor;
};

/**
 * Returns a unique string representation of the given date 'rounded' to the desired unit of time.
 * @param {Date} date - The date object to evaluate.
 * @param timeUnit - The unit of time to round to. Allowed values: 'year', 'month', 'week', 'day',
 * 'dayOfMonth', 'hourOfDay'
 * @returns {String} - The appropriate string value of the given Date, based on the given unit of time.
 */
export const timeUnitString = (date, timeUnit) => {
  const mDate = Moment(date);
  const hour = mDate.hour(); // 0-23
  const dayOfMonth = mDate.date(); // 1-31
  const day = mDate.dayOfYear(); // 1-366
  const week = mDate.week(); // 1-52
  const month = mDate.month(); // 0-11
  const year = mDate.year(); // 4 digit year

  // All keys are appended with year to ensure uniqueness of key (in case we're given a long time range).
  let timeUnitKey;
  switch (timeUnit) {
    case 'hourOfDay':
      // Hour of day. Format: hour-day-year. E.g. 23-365-2014, 4-125-1999, etc.
      timeUnitKey = `${hour}-${day}-${year}`;
      break;
    case 'dayOfMonth':
      // Day of month. Format: dayOfMonth-month-year. E.g. 28-11-2008, 31-4-2012, etc.
      timeUnitKey = `${dayOfMonth}-${month}-${year}`;
      break;
    case 'day':
      // Day of year. Format: dayOfYear-year. E.g. 365-2002, 147-1945, etc.
      timeUnitKey = `${day}-${year}`;
      break;
    case 'week':
      // Week of year. Format: week-year. E.g. 51-2006, 4-1998, etc.
      timeUnitKey = `${week}-${year}`;
      break;
    case 'month':
      // Month of year. Format: month-year. E.g. 2-1988, 11-2014, etc.
      timeUnitKey = `${month}-${year}`;
      break;
    case 'year':
      // 4 digit year. Format: year. E.g. 1945, 1999, 2017, etc.
      timeUnitKey = year;
      break;
    default:
      break;
  }

  return timeUnitKey;
};
