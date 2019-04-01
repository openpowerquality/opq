import { JsonRoutes } from 'meteor/simple:json-routes';
import moment from 'moment';

/**
 * Support the Health endpoint.
 */

JsonRoutes.add('get', '/health', function (req, res) {
  JsonRoutes.sendResult(res, {
    data: {
      name: 'view',
      ok: true,
      timestamp: Math.trunc(moment().valueOf() / 1000),
    },
  });
});
