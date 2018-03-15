import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import 'semantic-ui-css/semantic.css';
import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom';

// Components
import NavBar from '../../ui/components/NavBar.jsx';
import Example from '../../ui/pages/Example.jsx';
import Settings from '../../ui/pages/Settings.jsx';
import Account from '../../ui/pages/Account.jsx';
import NotFound from '../../ui/pages/NotFound.jsx';
import Signin from '../../ui/pages/Signin.jsx';
import Signup from '../../ui/pages/Signup.jsx';
import Signout from '../../ui/pages/Signout.jsx';
import DRS from '../../ui/pages/DRS.jsx';
import LandingPage from '../../ui/pages/LandingPage';

/** Top-level layout component for this application. Called in imports/startup/client/startup.jsx. */
class App extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <Router>
          <div>
            <NavBar />
            <Switch>
              <Route exact path="/" component={LandingPage} />
              <Route path="/signin" component={Signin} />
              <Route path="/signup" component={Signup} />
              <Route path="/drs" component={DRS} />
              <ProtectedRoute path="/example" component={Example} />
              <ProtectedRoute path="/account" component={Account} />
              <ProtectedRoute path="/settings" component={Settings} />
              <ProtectedRoute path="/signout" component={Signout} />
              <Route component={NotFound} />
            </Switch>
          </div>
        </Router>
    );
  }
}

/**
 * ProtectedRoute (see React Router v4 sample)
 * Checks for Meteor login before routing to the requested page, otherwise goes to signin page.
 * @param {any} { component: Component, ...rest }
 */
const ProtectedRoute = ({ component: Component, ...rest }) => (
    <Route
        {...rest}
        render={(props) => {
          const isLogged = Meteor.userId() !== null;
          return isLogged ?
              (<Component {...props} />) :
              (<Redirect to={{ pathname: '/signin', state: { from: props.location } }}/>
              );
        }}
    />
);

/** Require a component and location to be passed to each ProtectedRoute. */
ProtectedRoute.propTypes = {
  component: PropTypes.func.isRequired,
  location: PropTypes.object,
};

export default App;
