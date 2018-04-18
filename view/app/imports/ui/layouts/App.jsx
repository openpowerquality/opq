import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import 'semantic-ui-css/semantic.css';
import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { Roles } from 'meteor/alanning:roles';

// Pages
import NavBar from '../../ui/components/NavBar.jsx';
import NotFound from '../../ui/pages/NotFound.jsx';
import Signin from '../../ui/pages/Signin.jsx';
import About from '../../ui/pages/About.jsx';
import Signout from '../../ui/pages/Signout.jsx';
import Landing from '../../ui/pages/Landing';
import Profile from '../../ui/pages/Profile';
import Admin from '../../ui/pages/Admin';
import EditBox from '../../ui/pages/EditBox';
import LiveDataManager from '../../ui/pages/LiveDataManager';

/** Top-level layout component for this application. Called in imports/startup/client/startup.jsx. */
class App extends React.Component {
  render() { // eslint-disable-line class-methods-use-this
    return (
        <Router>
          <div>
            <NavBar />
            <Switch>
              <Route exact path="/" component={Landing} />
              <Route path="/about" component={About} />
              <AdminProtectedRoute path="/admin" component={Admin}/>
              <ProtectedRoute path="/profile" component={Profile}/>
              <ProtectedRoute path="/signout" component={Signout} />
              <ProtectedRoute path="/edit/:box_id" component={EditBox} />
              <ProtectedRoute path="/livedata" component={LiveDataManager} />
              <Route path="/signin" component={Signin} />
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


/**
 * AdminProtectedRoute (see React Router v4 sample)
 * Checks for Meteor login and admin role before routing to the requested page, otherwise goes to signin page.
 * @param {any} { component: Component, ...rest }
 */
const AdminProtectedRoute = ({ component: Component, ...rest }) => (
  <Route
    {...rest}
    render={(props) => {
      const isLogged = Meteor.userId() !== null;
      const isAdmin = Roles.userIsInRole(Meteor.userId(), 'admin');
      // For some reason, on browser refresh, isAdmin returns false even when logged in as admin.
      // So, admins go to the signin page on browser refresh even though they are logged in. Weird.
      return (isLogged && isAdmin) ?
        (<Component {...props} />) :
        (<Redirect to={{ pathname: '/signin', state: { from: props.location } }}/>
        );
    }}
  />
);


/** Require a component and location to be passed to each AdminProtectedRoute. */
AdminProtectedRoute.propTypes = {
  component: PropTypes.func.isRequired,
  location: PropTypes.object,
};

export default App;
