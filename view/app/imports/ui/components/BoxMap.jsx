import React from 'react';
import WidgetPanel from '../layouts/WidgetPanel';

/** Display system statistics. */
class BoxMap extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <WidgetPanel title="Box Map">
          <p>See <a href="https://github.com/openpowerquality/opq/issues/69">Issue 69</a> for details.</p>
        </WidgetPanel>
    );
  }
}

export default BoxMap;
