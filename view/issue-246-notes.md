# Issue 246 implementation notes

* Need to determine if we can dynamically retrieve the different incident types. (No, not at present.)

* Current design idea: 
  - create a Meteor method that is called with a start time.
  - this method generates a report on what incidents were generated since that start time.
  - The report includes:
    - How many incidents were generated during that time.
    - What boxes were involved in those incidents.
    - What incident types were involved in those incidents.
    - This report is returned as a JSON string: 
      { startTime: <milliseconds?>, totalIncidents: <integer>, incidentTypes: [<string>], boxIDs: [<integer>] }
      
* The current notifications system relies on waking up, checking health, and generating a Notification instance. However, for incidents, what makes more sense is to simply wakeup at the prescribed interval in time, run a report to see if there were any Incidents generated in the last time interval, and then email the results. The problem is that the "bell" doesn't make sense in this latter context. Since there are no notification records to view.  Maybe should get rid of the bell?

* We need to rewrite the notification email/text.  The new report says:

In the past [hour|day]:

  * System services ([Service]*) went down a total of [N] times.
  * [N] Incidents ([INCIDENT_TYPE]*) were generated at these locations: [LOCATIONS*]
         
       
