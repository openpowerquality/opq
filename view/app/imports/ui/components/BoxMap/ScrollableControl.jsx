import { DomEvent } from 'leaflet';
import React from 'react';
import PropTypes from 'prop-types';
import Control from 'react-leaflet-control';

// Scroll events seem to be ignored by the Control component and gets captured by the Leaflet Map component which
// it overlays. This component wraps the Control component and fixes this behavior by utilizing Leaflet's DomEvent.
// Adapted from: https://github.com/LiveBy/react-leaflet-control/issues/2
export default class ScrollableControl extends React.Component {
  constructor(props) {
    super(props);
    this.refContainer.bind(this);
  }

  refContainer(elem) {
    // This can be called multiple times due to React's rendering system, so we need to ensure we only mess with
    // the DomEvent once.
    if (!this.divRef && elem) {
      this.divRef = elem;
      DomEvent.disableClickPropagation(elem).disableScrollPropagation(elem);
    }
  }

  render() {
    const { position, children } = this.props;
    return (
        <Control position={position}>
          <div ref={this.refContainer.bind(this)}>
            {children}
          </div>
        </Control>
    );
  }
}

ScrollableControl.propTypes = {
  position: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

