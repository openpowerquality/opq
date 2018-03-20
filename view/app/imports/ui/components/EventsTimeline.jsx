import React from 'react';
import 'semantic-ui-css/semantic.css';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display system statistics. */
class EventsTimeline extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="Events Timeline">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/71">Issue 71</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default EventsTimeline;
