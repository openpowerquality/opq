import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Redirect } from 'react-router-dom';
import PropTypes from 'prop-types';

export default class Signout extends React.Component {
  render() {
    Meteor.logout();
    const { from } = this.props.location.state || { from: { pathname: '/' } };
    console.log(this.props.location.state);
    return (
      <Redirect to={from} />
    );
  }
}

Signout.propTypes = {
  location: PropTypes.object,
};
