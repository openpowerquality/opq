import { JsonRoutes } from 'meteor/simple:json-routes';
import moment from 'moment';

JsonRoutes.add('get', '/health', function (req, res) {
  JsonRoutes.sendResult(res, {
    data: {
      name: 'view',
      ok: true,
      timestamp: moment().valueOf(),
    },
  });
});
