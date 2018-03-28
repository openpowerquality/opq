import { Meteor } from 'meteor/meteor';
import { expect } from 'chai';
import { BoxOwners } from './BoxOwnersCollection';

/* eslint prefer-arrow-callback: "off", no-unused-expressions: "off" */
/* eslint-env mocha */

if (Meteor.isServer) {
  describe('BoxOwnersCollection', function testSuite() {
    before(function setup() {
      BoxOwners.removeAll();
    });

    after(function tearDown() {
      BoxOwners.removeAll();
    });

    it('#define, #findBoxesWithOwner, #findOwnersWithBox', function test() {
      const username = 'opq@hawaii.edu';
      const boxId = '1';
      const boxOwnerId1a = BoxOwners.define({ username, boxId });
      const boxOwnerId1b = BoxOwners.define({ username, boxId });
      expect(boxOwnerId1a).to.deep.equal(boxOwnerId1b);
      expect(BoxOwners.findBoxesWithOwner(username).length).to.equal(1);
      expect(BoxOwners.findOwnersWithBoxId(boxId)).to.deep.equal([username]);
      BoxOwners.removeBoxesWithOwner(username);
      expect(BoxOwners.findBoxesWithOwner(username)).to.be.empty;
      expect(BoxOwners.findOwnersWithBoxId(boxId)).to.be.empty;
    });
  });
}
