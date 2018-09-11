import React from 'react';
import PropTypes from 'prop-types';
import { Meteor } from 'meteor/meteor';
import { HashRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import { Roles } from 'meteor/alanning:roles';
import { ROLE } from '../../api/opq/Role';
import NavBar from '../../ui/components/NavBar.jsx';
import NotFound from '../../ui/pages/NotFound.jsx';
import Signin from '../../ui/pages/Signin.jsx';
import About from '../../ui/pages/About.jsx';
import Signout from '../../ui/pages/Signout.jsx';
import Landing from '../../ui/pages/Landing';
import Profile from '../../ui/pages/Profile';
import ManageBoxPage from '../../ui/pages/ManageBox/ManageBoxPage';
import ManageLocationPage from '../../ui/pages/ManageLocationPage';
import ManageRegionPage from '../../ui/pages/ManageRegionPage';
import ManageUserPage from '../pages/ManageUsers/ManageUserPage';
import BoxMapPage from '../../ui/pages/BoxMapPage';
import EditBoxPage from '../pages/ManageBox/EditBoxPage';
import NewBoxPage from '../pages/ManageBox/NewBoxPage';
import NewUserPage from '../pages/ManageUsers/NewUserPage';
import EditUserPage from '../pages/ManageUsers/EditUserPage';
import LiveDataManager from '../../ui/pages/LiveDataManager';
import Inspector from '../../ui/pages/Inspector';

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
              <AdminProtectedRoute path="/admin/manage/opqbox/new" component={NewBoxPage}/>
              <AdminProtectedRoute path="/admin/manage/user/new" component={NewUserPage}/>
              <AdminProtectedRoute path="/admin/manage/user/edit/:_id" component={EditUserPage}/>
              <AdminProtectedRoute path="/admin/manage/opqbox/edit/:box_id" component={EditBoxPage}/>
              <AdminProtectedRoute path="/admin/manage/opqbox" component={ManageBoxPage}/>
              <AdminProtectedRoute path="/admin/manage/location" component={ManageLocationPage}/>
              <AdminProtectedRoute path="/admin/manage/region" component={ManageRegionPage}/>
              <AdminProtectedRoute path="/admin/manage/user" component={ManageUserPage}/>
              <ProtectedRoute path="/profile" component={Profile}/>
              <ProtectedRoute path="/boxmap" component={BoxMapPage}/>
              <ProtectedRoute path="/signout" component={Signout} />
              <ProtectedRoute path="/livedata" component={LiveDataManager} />
              <ProtectedRoute path="/inspector" component={Inspector} />
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
      const isAdmin = Roles.userIsInRole(Meteor.userId(), ROLE.ADMIN);
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
