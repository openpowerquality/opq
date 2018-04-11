import React from 'react';
import 'semantic-ui-css/semantic.css';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display system statistics. */
class EventDetail extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="Event Detail">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/75">Issue 75</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default EventDetail;
