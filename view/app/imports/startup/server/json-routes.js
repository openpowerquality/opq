import { JsonRoutes } from 'meteor/simple:json-routes';
import moment from 'moment';

/**
 * Support the Health endpoint.
 * http://hostname/health now returns the required Health JSON string.
 * Note that the '#' in the route used by React Router is NOT present in this path.
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
