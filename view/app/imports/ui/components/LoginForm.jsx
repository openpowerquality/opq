import React from 'react';
import { AutoForm, TextField, SubmitField, ErrorsField } from 'uniforms-semantic';
import PropTypes from 'prop-types';

const LoginForm = ({ schema, onSubmit, model = {} }) => (
  <AutoForm schema={schema} onSubmit={onSubmit} model={model}>
    <TextField type="email" name="email" />
    <TextField type="password" name="password" />
    <SubmitField value="Log In"/>
    <ErrorsField />
  </AutoForm>
);

LoginForm.proptypes = {
  schema: PropTypes.object,
  onSubmit: PropTypes.func,
  model: PropTypes.object,
};

export default LoginForm;
