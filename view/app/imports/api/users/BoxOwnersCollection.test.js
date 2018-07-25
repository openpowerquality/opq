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

    it('#updateOwnersForBox', function test() {
      const user1 = 'opq1@hawaii.edu';
      const user2 = 'opq2@hawaii.edu';
      const user3 = 'opq3@hawaii.edu';
      const box1 = '1';
      BoxOwners.updateOwnersForBox(box1, [user1, user2]);
      expect(BoxOwners.findBoxesWithOwner(user1).length).to.equal(1);
      expect(BoxOwners.findOwnersWithBoxId(box1).length).to.equal(2);
      BoxOwners.updateOwnersForBox(box1, [user3]);
      expect(BoxOwners.findOwnersWithBoxId(box1)).to.deep.equal([user3]);
      BoxOwners.removeAll();
    });

    it('#updateBoxesWithOwner', function test() {
      const user1 = 'opq1@hawaii.edu';
      const box1 = '1';
      const box2 = '2';
      const box3 = '3';
      BoxOwners.updateBoxesWithOwner(user1, [box1, box2]);
      expect(BoxOwners.findBoxIdsWithOwner(user1).length).to.equal(2);
      expect(BoxOwners.findOwnersWithBoxId(box1).length).to.equal(1);
      BoxOwners.updateBoxesWithOwner(user1, [box3]);
      expect(BoxOwners.findBoxIdsWithOwner(user1)).to.deep.equal([box3]);
    });
  });
}
