import { Template } from 'meteor/templating';
import { Mongo } from 'meteor/mongo';
import { dataContextValidator } from '../../../utils/utils.js';
import { getEventMetaDataById } from '../../../api/events/EventsCollectionMethods.js'
import { getEventData } from '../../../api/box-events/BoxEventsCollectionMethods.js';
import { getEventDataFSData } from '../../../api/eventDataFS/EventDataFSCollectionMethods.js';
import Dygraph from 'dygraphs';
import '../../../../client/lib/misc/dygraphSynchronizer.js';
import './eventView.html';
import '../eventWaveformChart/eventWaveformChart.js';

Template.eventView.onCreated(function() {
  const template = this;

  dataContextValidator(template, new SimpleSchema({
    eventMetaDataId: {type: Mongo.ObjectID, optional: true} // Optional b/c waiting on user to select event.
  }), null);

  template.currentEventMetaData = new ReactiveVar();
  template.currentEventData = new ReactiveVar([]);
  template.isLoadingEventData = new ReactiveVar(false);
  template.dygraphInstances = [];
  template.dygraphSync = null;

  // Retrieve document of given event meta data id.
  template.autorun(() => {
    const eventMetaDataId = Template.currentData().eventMetaDataId;
    if (eventMetaDataId) {
      // Clear old event data first.
      template.currentEventData.set([]);

      // Then retrieve new meta data.
      template.isLoadingEventData.set(true);
      getEventMetaDataById.call({eventMetaDataId}, (error, eventMetaData) => {
        template.isLoadingEventData.set(false);
        if (error) {
          console.log(error);
        } else {
          template.currentEventMetaData.set(eventMetaData);
          // console.log('CurrentEventMetaData: ', eventMetaData);
        }
      })
    }
  });

  // Retrieve event data for current event.
  template.autorun(() => {
    const currentEventMetaData = template.currentEventMetaData.get();
    if (currentEventMetaData) {
      const event_number = currentEventMetaData.event_number;
      const boxes_received = currentEventMetaData.boxes_received;

      boxes_received.forEach(box_id => {
        template.isLoadingEventData.set(true);
        getEventData.call({event_number, box_id}, (error, eventData) => {
          template.isLoadingEventData.set(false);
          if (error) {
            console.log(error);
          } else {
            // Now have to get waveform data from GridFs.
            getEventDataFSData.call({filename: eventData.data}, (error, result) => {
              if (error) {
                console.log(error);
              } else {
                eventData.waveform = result;
                const currentEventData = template.currentEventData.get();
                currentEventData.push(eventData);
                template.currentEventData.set(currentEventData);
              }
            });
          }
        });
      });
    }
  });
});

Template.eventView.onRendered(function() {
  const template = this;

  // template.$('#eventData-modal').modal(); // Init modal.
});

Template.eventView.helpers({
  eventData() {
    const eventData = Template.instance().currentEventData.get(); // Array of all event data.
    return eventData;
  },
  dygraphSynchronizer() {
    const template = Template.instance();
    return (graph) => {
      template.dygraphInstances.push(graph);
      template.dygraphSync = Dygraph.synchronize(template.dygraphInstances);
    }
  },
  calibratedWaveformData(box_id, waveformData) {
    // Need to store these values in db.
    const boxCalibrationConstants = {
      1: 152.1,
      3: 154.20,
      4: 146.46
    };
    const constant = boxCalibrationConstants[box_id] || 1;
    const calibratedData = waveformData.map(val => val/constant);
    return calibratedData;
  },
  isLoadingEventData() {
    return Template.instance().isLoadingEventData.get();
  }
});

Template.eventView.events({
  'click .ui.button': function(event, template) {
    const box_id = event.currentTarget.id.replace('-button', '');
    template.$(`#${box_id}-modal`).modal({detachable: false}).modal('show');
  }
});

