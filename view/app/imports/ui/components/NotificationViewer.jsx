import React from 'react';
import { Meteor } from 'meteor/meteor';
import { Feed, Icon, Popup, Header, Divider, Label, Container } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import { withTracker } from 'meteor/react-meteor-data';
import { Link } from 'react-router-dom';
import { Notifications } from '../../api/notifications/NotificationsCollection';

/* eslint max-len:0 */

class NotificationViewer extends React.Component {

  /** Renders a popup that displays all of the user's notifications */
  render() {
    const divStyle = { color: '#2185D0', paddingLeft: '2px', fontWeight: 'bold' };
    const feedStyle = {
      maxHeight: 200,
      width: 300,
      overflow: 'auto',
      padding_top: '1em',
      padding_bottom: '1em',
    };

    return (
        <Container fluid>
          <Popup trigger={<Icon name='bell' style={divStyle}/>}
                 on='click'
                 position='bottom right'
          >
            <Header>
              Notifications
            </Header>
            <Divider/>
            <Container style={feedStyle} fluid>
              <Feed>
                { (this.props.userNotifications).length > 0 ? (this.props.userNotifications.map((notification) =>
                    <Feed.Event
                        key={notification._id}
                        icon='exclamation circle'
                        date={notification.timestamp.toLocaleString()}
                        summary={notification.data}/>)) : <Feed.Extra content='No notifications yet'/>}
              </Feed>
            </Container>
            <Divider hidden/>
            <Label attached='bottom' size='small'>
              <Link to={'/profile/'}> <Icon name='setting'/>Manage Notifications</Link>
            </Label>
          </Popup>
        </Container>
    );
  }
}

NotificationViewer.propTypes = {
  ready: PropTypes.bool.isRequired,
  userNotifications: PropTypes.array,
};

export default withTracker(() => {
  const notificationsSub = Meteor.subscribe(Notifications.getPublicationName());
  const username = Meteor.user().username;
  return {
    ready: notificationsSub.ready(),
    userNotifications: Notifications.findNotificationsByUser(username),
  };
})(NotificationViewer);
