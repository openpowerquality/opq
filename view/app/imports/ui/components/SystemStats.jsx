import React from 'react';
import 'semantic-ui-css/semantic.css';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display system statistics. */
class SystemStats extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="System Stats">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/70">Issue 70</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default SystemStats;
