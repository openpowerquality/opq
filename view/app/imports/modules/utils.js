import { Meteor } from 'meteor/meteor';

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
  let totalVal = total - 1; // Assuming 0 based counting.

  if (!timerHandle) {
    timerHandle = Meteor.setInterval(() => {
      progressBarPrinter(currentVal, totalVal, '=', 30, message);
    }, updateRate);
  }

  return {
    clearInterval() {
      if (timerHandle) Meteor.clearInterval(timerHandle);
      process.stdout.write('\n'); // Final newline after progressBarPrinter is done.
    },
    updateBar(newCurrent) {
      currentVal = newCurrent;
    }
  }

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
  let progressBar = Array.from(' '.repeat(maxTicks+2));
  progressBar[0] = '[';
  progressBar[progressBar.length-1] = ']';

  const progressPercentage = (current / total) * 100;
  const currentBars = maxTicks * (progressPercentage / 100.0);
  progressBar.fill(tickChar, 1, currentBars + 1);
  process.stdout.write('\033[F'); // ANSI code to move cursor up one line.
  process.stdout.write(`\n\r${message} ${progressBar.join('')} (${progressPercentage.toFixed(1)}%)`);
}