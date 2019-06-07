import { Meteor } from 'meteor/meteor';
import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { CallPromiseMixin } from 'meteor/didericis:callpromise-mixin';
import SimpleSchema from 'simpl-schema';
// import { LahaConfig } from './LahaConfigCollection';
import { MakaiConfig } from '../makai-config/MakaiConfigCollection';

export const getMakaiConfig = new ValidatedMethod({
    name: 'MakaiConfig.getMakaiConfig',
    mixins: [CallPromiseMixin],
    validate: new SimpleSchema({}).validator({ clean: true }),
    run() {
        if (Meteor.isServer) {
            return MakaiConfig.find({}).fetch();
        }
        return null;
    },
});
