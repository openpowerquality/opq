import React from 'react';
import 'semantic-ui-css/semantic.css';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display data from each box in real time.. */
class LiveBoxMonitor extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="Live Box Monitor">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/76">Issue 76</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default LiveBoxMonitor;
