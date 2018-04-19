# Deploy Health

The goal of the OPQHealth service is provide a diagnostic facility for determining whether or not all of the OPQ services appear to be running appropriately.  It does this by monitoring various aspects of the system and publishing its findings to a log file and mongodb.

## 1. Prelude: account setup

Here are one-time configuration activities required to do deployment of OPQHealth.

#### 1.1 Obtain the opquser account credentials

OPQHealth is deployed using the opquser account.  You need to obtain the password for opquser in order to do this deployment.

#### 1.2 Set up ssh without password prompt

In order to use the scripts to transfer files, you need to set up SSH login without a password.  You can follow [these instructions](http://www.linuxproblem.org/art_9.html).

To check to make sure you have set up your SSH keys correctly, bring up a new console and run the following command:

```
ssh -p 29862 opquser@emilia.ics.hawaii.edu
```

This should log you into emilia without prompting you for a password, with output like the following:

```
The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Sun Apr  8 07:57:57 2018 from cpe-66-91-216-204.hawaii.res.rr.com
opquser@emilia:~$
```

#### 2.1 Build the production bundle

In general, you will build the production bundle from the master branch of OPQHealth.

In your development environment, be sure you are in the master branch, then change directories into the `opq/health/` directory.

The contents of the `opq/health/deploy/` directory should contain the following files:
  * deploy-run.sh:  A script for running the deployment on the server.
  * deploy-transfer.sh: A script for copying the appropriate files to the server.

#### 2.2 Copy deployment files to the server

To copy deployment files to the server, invoke the `deploy-transfer.sh` script. This script creates a new directory whose name is the current timestamp, copies config.json, deploy-run.sh, and health.py into it, then gzips that directory and secure copies it to emilia.

Here is what the invocation of this command should look like:

```
./deploy-transfer.sh
++ date +%Y%m%d_%H%M%S
+ timestamp=20180408_083036
+ mkdir 20180408_083036
+ cp deploy-run.sh 20180408_083036
+ cp ../health.py 20180408_083036
+ cp ../config.json 20180408_083036
+ cp ../protobuf 20180408_083036 -r
+ tar czf 20180408_083036.tar.gz 20180408_083036
+ rm -rf 20180408_083036
+ scp -P 29862 20180408_083036.tar.gz opquser@emilia.ics.hawaii.edu:health
20180408_083036.tar.gz                                                                                                100%   43MB   1.5MB/s   00:29    
+ set +x
```

## 3. Server-side deployment tasks

Now ssh to the server to do the remainder of the deployment:

```
ssh -p 29862 opquser@emilia.ics.hawaii.edu
```

#### 3.1 Unpack tar file with latest release

```
$ tar xvf 20180408_085449.tar.gz
```  

Change directories into the health/ subdirectory, and list the files:

```
$ cd health
$ ls -la
ls -la
total 43572
drwxr-xr-x  3 opquser opquser     4096 Apr  8 08:55 .
drwxr-xr-x 10 opquser opquser     4096 Apr  8 08:50 ..
-rw-r--r--  1 opquser opquser 44601734 Apr  8 08:55 20180408_085449.tar.gz
```

#### 3.2 Kill the current OPQHealth process

Find the PID of the current process running OPQHealth process this way:

```
$ ps -ef | grep python3
opquser  10645     1  1 08:56 pts/3    00:00:08 python3 health.py
opquser  12875 18406  0 09:07 pts/3    00:00:00 grep python3
```

In this case, the PID is 10645. Kill that process with the following command:

```
$ kill -9 10645
```

#### 3.3 Verify that the server is running the correct version of python3

Check that python3 is currently installed:

```
$ python3 --version
Python 3.4.2
```

If this throws any errors, install python3 before proceeding.

#### 3.4 Run the new version of OPQView

To run the new version of OPQHealth, invoke the deploy-run.sh script:

```
$ ./deploy-run.sh
```

This script brings up OPQHealth in the background (so that you can exit this terminal session), and sends all output to the files nohupout.txt and logfile.txt. To check that the system came up normally, you can print out the contents of the nohupout and logfile.
