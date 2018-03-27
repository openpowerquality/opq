import React from 'react';
import { Container, Header } from 'semantic-ui-react';

const About = () => (
    <Container text>
      <Header as="h1">About OPQ</Header>
      <p>Welcome to Open Power Quality.</p>
      <p>The goal of Open Power Quality is to support the continued growth in use of renewable energy sources in Hawaii
        and elsewhere through a novel triple open source combination of hardware, software, and power quality data. We
        are designing and implementing a low cost, consumer-grade hardware device called OPQBox for power quality whose
        specifications are available through an open source license. Each OPQBox can capture power quality data and send
        it to an instance of OPQHub, our cloud-based, software service, whose source code is also available as open
        source. Finally, the collected information will be available as “open data”, facilitating analysis and
        innovation.</p>
      <p>Our major project goals include:</p>
      <p><em>Low-cost, residential-level power quality monitoring.</em> Our target price for the hardware is under $40.
        Current commercial solutions are $200 and up. Our hardware specifications will be made available under
        open-source licensing to promote innovation and even lower costs.</p>
      <p><em>Point-of-use power quality data.</em> Traditionally, utilities were responsible for all power generation,
        and so they were also responsible for power quality monitoring. Such monitoring traditionally occurs at the
        substation, with the assumption that this reflects the quality of power experienced by the hundreds or thousands
        of end-users serviced by the substation. As end-users become both consumers and producers of power, the
        substation assumption is no longer valid, and it becomes important to know power quality as experienced by the
        end-user.</p>
      <p><em>Crowd-sourced grid-level acquisition of power quality data.</em> A key feature of our approach is to upload
        power quality data from end-users to a cloud-based service. Such crowd-sourcing can reveal trends and
        explanations for power quality not available to individuals.</p>
      <p><em>Crowd-sourced analysis of power quality data.</em> The creation of open data and its availability through
        an API to our cloud-based service creates an open-ended opportunity for analyses and combination with other data
        sources (such as cloud-cover and weather data).</p>
      <p><em>Protection of end-user privacy.</em> Open Power Quality creates a technical and social challenge: how to
        allow end-users to share their power quality data with others (to reap the benefits of crowd-sourcing) while not
        forcing them to reveal more than they wish about themselves and their location? Our software service will
        provide various privacy protection capabilities to enable end-users to share data in a way with which they feel
        comfortable.</p>
      <p>We believe our combination of open hardware, software, and data provides a compelling and complementary
        alternative to traditional, utility-based data collection, analysis, and management. It creates a path to active
        engagement by end-users in the development of a reliable, high quality grid.</p>
      <p>For more information about OPQ, please visit our website at <a
          href="http://openpowerquality.org/">http://openpowerquality.org</a></p>
    </Container>
);

export default About;
