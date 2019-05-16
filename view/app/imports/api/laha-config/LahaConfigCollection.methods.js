import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
import { LahaConfig } from './LahaConfigCollection';

export const getLahaConfig = new ValidatedMethod({
    name: 'LahaConfig.getLahaConfig',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({}).validator({ clean: true }),
    run() {
        if (Meteor.isServer) {
            return LahaConfig.find({}).fetch();
        }
        return null;
    },
});
