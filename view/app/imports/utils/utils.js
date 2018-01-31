import { check } from 'meteor/check';
import Moment from 'moment';


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
