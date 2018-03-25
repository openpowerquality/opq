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
      const username1 = 'opq@hawaii.edu';
      const boxId1 = 1;
      const boxOwnerId1a = BoxOwners.define({ username: username1, boxId: boxId1 });
      const boxOwnerId1b = BoxOwners.define({ username: username1, boxId: boxId1 });
      expect(boxOwnerId1a).to.deep.equal(boxOwnerId1b);
      expect(BoxOwners.findBoxesWithOwner(username1)).to.deep.equal([boxId1]);
      expect(BoxOwners.findOwnersWithBox(boxId1)).to.deep.equal([username1]);
    });
  });
}
