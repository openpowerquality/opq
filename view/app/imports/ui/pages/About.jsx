import React from 'react';
import { Container, Header } from 'semantic-ui-react';

const About = () => (
    <Container text>
      <Header as="h1">About OPQ</Header>
      <p>Welcome to Open Power Quality.</p>
      <p>The Open Power Quality project began in 2012 with the goal of developing and evaluating technology to support
          three important improvements to electrical infrastructure:</p>
      <ol>
        <li>Increase the capacity of small and large electrical grids to employ distributed, intermittent forms of
            renewable energy.</li>
        <li>Gain insight into lifespan and failure rate problems in consumer electronics due to poor power quality.</li>
        <li>Provide an independent, low cost source of useful power quality data to consumers, researchers, and public
            policy makers.</li>
      </ol>
      <p>For more information about OPQ, please visit our website at <a
          href="http://openpowerquality.org/">http://openpowerquality.org</a>, which has much more information on the
          history, current status, and future goals of the project.</p>
    </Container>
);

export default About;
