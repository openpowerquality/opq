// A module to contain our Higher Order Components (HOCs).
// Unsure whether it is more appropriate for this to be a .jsx file instead of a .js file. Since we are not
// actually exporting React components directly, but rather functions that return a React component, it seemed more
// logical to keep this as a .js file. However, Intellij complains of syntax errors because we have JSX code in
// a regular .js file - so keeping this as a .jsx file for now.
import React from 'react';

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
