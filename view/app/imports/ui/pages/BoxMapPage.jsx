import React from 'react';
import { Grid } from 'semantic-ui-react';
import BoxMap from '../components/BoxMap/BoxMap';
import WidgetPanel from '../layouts/WidgetPanel';

const helpText = `
<p>The Box Map component allows you to view the location of your OPQBoxes on an interactive map.</p>

<p>The <b>Data Display</b> button on the top-right corner of the map gives you the following options:
<br />
<b>Measurement Type</b>: The type of measurement data to display next to each OPQBox displayed on the map.
<br />
<b>Box Location Granularity</b>: Set the location of OPQBoxes on the map based either on the box's exact coordinates, or
the box's region. The latter option is useful in that it will cluster all OPQBoxes into their respective regions,
allowing you to view a region's average measurement data.
</p>

<p>The panel on the left side of the map lists all of the OPQBoxes connected to your account. The dropdown box
at the top of this panel allows you to filter your OPQBoxes based on any given region or location</p>
<p>Each OPQBox item in the side panel has a set of buttons that can help you in the following ways:
<br />
<b>Zoom to Box</b>: Finds and zooms to this OPQBox on the map.
<br />
<b>View Additional Box Details</b>: Display additional information about this OPQBox.
<br />
<b>Box Settings</b>: Edit this box's settings.
<br />
<b>View Box Events</b>: See all PQ events for this OPQBox
<br />
<b>View Box Measurements and Trends</b>: See the trends and measurements for this OPQBox.
</p>
`;

const BoxMapPage = () => (
    <Grid container stackable>
      <Grid.Column width={16}>
        <WidgetPanel title="Box Map" noPadding={true} helpText={helpText}>
          <BoxMap/>
        </WidgetPanel>
      </Grid.Column>
    </Grid>
);

export default BoxMapPage;
