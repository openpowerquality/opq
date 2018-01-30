# OPQView Installation

## Installation

First, [install Meteor](https://www.meteor.com/install).

Second, [download a copy of OPQ](https://github.com/openpowerquality/opq/archive/master.zip), or clone it using git.
  
Third, cd into the app/ directory and install libraries with:

```
$ meteor npm install
```

Then, download the latest OPQ mongodump file at:
Unpack the tar.gz, place the opq folder into the view directory.
Before we can run the mongorestore command, we must run the local Meteor application so that its MongoDB instance is
running. In order to do this, run the app with:
```
meteor npm run start
```
And then in another terminal window, cd to the same directory where the opq dump file is located, and run:

```
mongorestore -h 127.0.0.1 --port 3001 --gzip -d meteor opq
```

Finally, run the system with:

```
$ meteor npm run start
```

If all goes well, the application will appear at [http://localhost:3000](http://localhost:3000). If you have an account on the UH test CAS server, you can login.  


