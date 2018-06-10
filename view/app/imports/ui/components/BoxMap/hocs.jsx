// A module to contain our Higher Order Components (HOCs).
// Unsure whether it is more appropriate for this to be a .jsx file instead of a .js file. Since we are not
// actually exporting React components directly, but rather functions that return a React component, it seemed more
// logical to keep this as a .js file. However, Intellij complains of syntax errors because we have JSX code in
// a regular .js file - so keeping this as a .jsx file for now.
import React from 'react';
import PropTypes from 'prop-types';
import { withRouter } from 'react-router-dom';
import _ from 'lodash';

// Simple HOC that wraps a component with a new component that has the passed in state. This essentially serves as
// a reusable React container component.
//
// Use case: Maintaining state outside of the withTracker HOC.
// The main issue is that the function we pass into withTracker() is just a single Tracker computation.
// As such, we cannot maintain state within that function because it will simply be overridden whenever the computation
// is invalidated (ie. from subscriptions). We need a container to maintain state outside of withTracker().
// With Blaze, we could easily do this from the template's onCreated function - where we could create template-level
// state variables and as many Tracker Autoruns as we needed (one of which would always be for the subscription).
// This would also allow us to use component state to change the component's subscription.
// Sidenote: We could also accomplish all of this by using a ReactiveVar/ReactiveDict/Sessions, but we would have
// to create module-level variables in our .jsx files, which seemed like the incorrect way to go. With higher order
// components, we have a pure React solution to this problem.
export function withStateContainer(initialStateObj) {
  return function (WrappedComponent) {
    class WithStateContainer extends React.Component {
      constructor(props) {
        super(props);
        this.state = initialStateObj;
        this.setContainerState = this.setContainerState.bind(this);
      }

      setContainerState(newState) {
        this.setState(newState);
      }

      render() {
        return <WrappedComponent setContainerState={this.setContainerState} {...this.state} {...this.props} />;
      }
    }

    // Give the component a more useful display name for debugging purposes.
    WithStateContainer.displayName = `WithStateContainer(${WrappedComponent.displayName || WrappedComponent.name
    || 'Component'})`;

    return WithStateContainer;
  };
}

// HOC that allows us to provide additional context to the given component.
// See: https://stackoverflow.com/questions/43465480/react-router-link-doesnt-work-with-leafletjs/43594791
export function withContext(WrappedComponent, context) {
  class ContextProvider extends React.Component {
    getChildContext() {
      return context;
    }

    render() {
      return <WrappedComponent {...this.props} />;
    }
  }

  ContextProvider.childContextTypes = {};
  Object.keys(context).forEach(key => {
    ContextProvider.childContextTypes[key] = PropTypes.any.isRequired;
  });

  return ContextProvider;
}

// Higher order component that will retrieve the given keys from React Router's Location state object and, if present,
// pass them as props into the wrapped component.
export function withRouterLocationStateAsProps(stateKeysAsProps, clearState = false) {
  return function (WrappedComponent) {
    class WithRouterLocationStateCleared extends React.Component {
      constructor(props) {
        super(props);
        this.state = {};
        this.currRouterLocationState = (props.location && props.location.state) ? props.location.state : null;
        this.currRouterLocationPathname = (props.location && props.location.pathname) ? props.location.pathname : null;
      }

      // FYI: Calling setState in this method will NOT cause an additional render to occur.
      // See: https://reactjs.org/docs/react-component.html#unsafe_componentwillmount
      UNSAFE_componentWillMount() {
        // Build the object that we will pass as props to the wrapped component.
        if (this.currRouterLocationState && stateKeysAsProps.length) {
          const locStateAsProps = {};
          stateKeysAsProps.forEach(key => {
            // Ensure that key actually exists in Router state. We want to avoid passing undefined props into the
            // wrapped component.
            const keyExists = Object.prototype.hasOwnProperty.call(this.currRouterLocationState, key);
            if (keyExists) locStateAsProps[key] = this.currRouterLocationState[key];
          });

          // Don't call setState if object is empty.
          if (Object.keys(locStateAsProps).length) this.setState(locStateAsProps);
        }

        // Experimental: The router's Location.state object will actually persist on page reload. If we don't want this
        // behavior for whatever reason, we can 'clear' the appropriate state keys. This option is disabled by default.
        if (clearState && this.currRouterLocationPathname && this.currRouterLocationState
            && Object.keys(this.currRouterLocationState).length) {
          const newState = _.omit(this.currRouterLocationState, stateKeysAsProps);
          this.props.history.replace({
            pathname: this.currRouterLocationPathname,
            state: newState,
          });
        }
      }

      render() {
        return <WrappedComponent {...this.state} {...this.props} />;
      }
    }

    // WithRouter's provided props.
    WithRouterLocationStateCleared.propTypes = {
      match: PropTypes.object.isRequired,
      location: PropTypes.object.isRequired,
      history: PropTypes.object.isRequired,
    };

    // Give the component a more useful display name for debugging purposes.
    WithRouterLocationStateCleared.displayName = `WithRouterLocationStateCleared(${WrappedComponent.displayName
      || WrappedComponent.name || 'Component'})`;

    return withRouter(WithRouterLocationStateCleared);
  };
}
