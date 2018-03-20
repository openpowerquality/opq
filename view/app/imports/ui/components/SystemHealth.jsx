import React from 'react';
import 'semantic-ui-css/semantic.css';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display system statistics. */
class SystemHealth extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="System Health">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/87">Issue 87</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default SystemHealth;
