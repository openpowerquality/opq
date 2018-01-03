import { Meteor } from 'meteor/meteor';
import { chai } from 'meteor/practicalmeteor:chai';

if (Meteor.isServer) {
  describe('Example Tests', function() {
    it('should have a value of "Hello World"', function() {
      const hw = 'Hello World';
      chai.expect(hw).to.equal('Hello World');
    });

    it('should add up to 42', function() {
      const sum = 10 + 40 - 8;
      chai.expect(sum).to.equal(42);
    });
  });
}