# OPQView Installation

This chapter explains how to install the OPQView system for development purposes. Installation instructions for deployed instances will be provided shortly.

## Install Meteor

First, [install Meteor](https://www.meteor.com/install).


## Install and run OPQ

Now [download a copy of OPQ](https://github.com/openpowerquality/opq/archive/master.zip), or clone it using git.
  
Next, cd into the app/ directory and install libraries with:

```
$ meteor npm install
```

Now bring up the OPQ system using:

```
meteor npm run start
```

## (Optional) Install a DB snapshot

It is useful but not mandatory to seed your development version of OPQ with a snapshot of OPQ data. Here are the steps to do so. 

First, [install MongoDB](https://docs.mongodb.com/manual/installation/).  Even though Meteor comes with a copy of Mongo, you will need to install MongoDB in order to run the mongorestore command.  

Second, download the snapshot of an OPQ database from [here](https://goo.gl/ZV2DNF). Note that it is 800MB compressed, so this might take a while.

Third, uncompress the downloaded tar.gz file. (Typically, double-clicking the file name will do the trick.) This will create a directory called "opq".

Fourth, make sure the OPQ system is running (i.e. `meteor npm run start`). This is required in order to ensure that MongoDB is running.

Fifth, bring up a new command shell, then cd to the directory containing the "opq" snapshot directory, and run:

```
mongorestore -h 127.0.0.1 --port 3001 --gzip -d meteor opq
```

Here is an excerpt of the sample output from running the above command. It takes around 3 minutes on a late model Mac laptop:

```
mongorestore -h 127.0.0.1 --port 3001 --gzip -d meteor opq
2018-01-29T14:50:49.999-1000	the --db and --collection args should only be used when restoring from a BSON file. Other uses are deprecated and will not exist in the future; use --nsInclude instead
2018-01-29T14:50:49.999-1000	building a list of collections to restore from opq dir
2018-01-29T14:50:50.001-1000	reading metadata for meteor.fs.chunks from opq/fs.chunks.metadata.json.gz
2018-01-29T14:50:50.001-1000	reading metadata for meteor.trends from opq/trends.metadata.json.gz
2018-01-29T14:50:50.001-1000	reading metadata for meteor.box_events from opq/box_events.metadata.json.gz
2018-01-29T14:50:50.001-1000	reading metadata for meteor.measurements from opq/measurements.metadata.json.gz
2018-01-29T14:50:50.089-1000	restoring meteor.fs.chunks from opq/fs.chunks.bson.gz
2018-01-29T14:50:50.158-1000	restoring meteor.box_events from opq/box_events.bson.gz
2018-01-29T14:50:50.217-1000	restoring meteor.trends from opq/trends.bson.gz
2018-01-29T14:50:50.277-1000	restoring meteor.measurements from opq/measurements.bson.gz
2018-01-29T14:50:52.994-1000	[........................]     meteor.fs.chunks   15.7MB/632MB   (2.5%)
2018-01-29T14:50:52.994-1000	[#######.................]    meteor.box_events  30.1MB/92.8MB  (32.4%)
2018-01-29T14:50:52.994-1000	[##......................]        meteor.trends  3.36MB/37.5MB   (8.9%)
2018-01-29T14:50:52.994-1000	[#.......................]  meteor.measurements  1.89MB/37.3MB   (5.1%)
2018-01-29T14:50:52.994-1000	
2018-01-29T14:50:55.994-1000	[#.......................]     meteor.fs.chunks   30.7MB/632MB   (4.8%)
2018-01-29T14:50:55.994-1000	[##############..........]    meteor.box_events  56.8MB/92.8MB  (61.2%)
2018-01-29T14:50:55.994-1000	[####....................]        meteor.trends  6.33MB/37.5MB  (16.9%)
2018-01-29T14:50:55.994-1000	[##......................]  meteor.measurements  3.62MB/37.3MB   (9.7%)
2018-01-29T14:50:55.994-1000	
2018-01-29T14:50:58.992-1000	[#.......................]     meteor.fs.chunks   44.9MB/632MB   (7.1%)
2018-01-29T14:50:58.992-1000	[######################..]    meteor.box_events  85.4MB/92.8MB  (92.0%)
2018-01-29T14:50:58.992-1000	[#####...................]        meteor.trends  9.09MB/37.5MB  (24.2%)
2018-01-29T14:50:58.992-1000	[###.....................]  meteor.measurements  5.11MB/37.3MB  (13.7%)
2018-01-29T14:50:58.992-1000	
2018-01-29T14:51:00.262-1000	[########################]  meteor.box_events  92.8MB/92.8MB  (100.0%)
2018-01-29T14:51:00.262-1000	restoring indexes for collection meteor.box_events from metadata
2018-01-29T14:51:00.858-1000	finished restoring meteor.box_events (13610 documents)
2018-01-29T14:51:00.858-1000	reading metadata for meteor.fs.files from opq/fs.files.metadata.json.gz
2018-01-29T14:51:00.976-1000	restoring meteor.fs.files from opq/fs.files.bson.gz
2018-01-29T14:51:01.801-1000	restoring indexes for collection meteor.fs.files from metadata
2018-01-29T14:51:01.992-1000	[#.......................]     meteor.fs.chunks   52.4MB/632MB   (8.3%)
2018-01-29T14:51:01.992-1000	[######..................]        meteor.trends  10.4MB/37.5MB  (27.9%)
2018-01-29T14:51:01.992-1000	[###.....................]  meteor.measurements  5.88MB/37.3MB  (15.8%)
2018-01-29T14:51:01.992-1000	

                  (many lines deleted)

2018-01-29T14:52:22.992-1000	[####################....]  meteor.fs.chunks  546MB/632MB  (86.4%)
2018-01-29T14:52:25.992-1000	[#####################...]  meteor.fs.chunks  561MB/632MB  (88.8%)
2018-01-29T14:52:28.993-1000	[#####################...]  meteor.fs.chunks  576MB/632MB  (91.1%)
2018-01-29T14:52:31.992-1000	[######################..]  meteor.fs.chunks  592MB/632MB  (93.6%)
2018-01-29T14:52:34.992-1000	[#######################.]  meteor.fs.chunks  608MB/632MB  (96.1%)
2018-01-29T14:52:37.995-1000	[#######################.]  meteor.fs.chunks  623MB/632MB  (98.5%)
2018-01-29T14:52:39.804-1000	[########################]  meteor.fs.chunks  632MB/632MB  (100.0%)
2018-01-29T14:52:39.804-1000	restoring indexes for collection meteor.fs.chunks from metadata
2018-01-29T14:53:01.999-1000	finished restoring meteor.fs.chunks (55639 documents)
2018-01-29T14:53:01.999-1000	done
```

## View OPQView

Finally, take a look at OPQView by going to http://localhost:3000. Here is what you should see:

<img src="opqview-home.png" >

Note that since this database snapshot was dumped more than one minute ago, all of the OPQBoxes will be interpreted as "offline".  This is because that status is determined based upon whether or not there is a Measurement document available for that OPQBox with a timestamp less than one minute in the past. At some point in the future, we will provide developer tools that simulate the production of measurement data in order to provide a more realistic development environment. 

