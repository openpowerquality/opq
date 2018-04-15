# Deploy Mauka

OPQMauka is a distributed middleware implemented in Python that provides high level PQ analysis for OPQ.

There are basically three steps to deploying OPQMauka: building the production bundle (a Python application) on a development machine, installing OPQMauka on the production machine, and managing the OPQMauka service.

## 1. Prelude: account setup

Here are one-time configuration activities required to do deployment of OPQMauka. 

#### 1.1 Obtain the opquser account credentials

OPQMauka is deployed using the opquser account.  You need to obtain the password for opquser in order to do this deployment.

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

## 2. Developer system deployment tasks

Do the following in your development environment. 

#### 2.1 Build and deploy the production bundle

In general, you will build the production bundle from the master branch of OPQMauka. 

In your development environment, be sure you are in the master branch, then change directories into the `opq/mauka/deploy/` directory.

This directory contains the following items:

* deploy-transfer.sh: Builds OPQMauka bundle and transfers to emilia.
* deploy-run.sh: Installs the OPQMauka service and utilities on emilia.
* mauka-service.sh: Service file that gets installed as system service.
* mauka-cli.sh: Utility script for starting the mauka command line interface.
* mauka-log.sh: Utility script for viewing mauka log. 
* [timestamp].tar.bz2 (local copies of created bundles)

Now invoke `./deploy-transfer.sh`:

This script builds a OPQMauka bundle from the current branch as a compressed tar.bz2 archive. Once the archive is built, the script will copy the bundle to the server via SCP.

The following is an example run performed on one of our development machines.

```
+ cd ../..
++ date +%Y%m%d_%H%M%S
+ TIMESTAMP=20180410_131135
+ mkdir -p mauka/deploy/20180410_131135
+ mkdir -p mauka/deploy/20180410_131135/mauka
+ cp -r mauka/constants mauka/deploy/20180410_131135/mauka
+ cp -r mauka/mongo mauka/deploy/20180410_131135/mauka
+ cp -r mauka/plugins mauka/deploy/20180410_131135/mauka
+ cp -r mauka/protobuf mauka/deploy/20180410_131135/mauka
+ cp mauka/config.json mauka/deploy/20180410_131135/mauka
+ cp mauka/OpqMauka.py mauka/deploy/20180410_131135/mauka
+ cp mauka/requirements.txt mauka/deploy/20180410_131135/mauka
+ mkdir -p mauka/deploy/20180410_131135/scripts
+ cp mauka/deploy/mauka-cli.sh mauka/deploy/20180410_131135/scripts
+ cp mauka/deploy/mauka-log.sh mauka/deploy/20180410_131135/scripts
+ cp mauka/deploy/mauka-service.sh mauka/deploy/20180410_131135/scripts
+ cp mauka/deploy/deploy-run.sh mauka/deploy/20180410_131135
+ tar cvjf mauka/deploy/20180410_131135.tar.bz2 -C mauka/deploy 20180410_131135
20180410_131135/
20180410_131135/deploy-run.sh
20180410_131135/mauka/
20180410_131135/mauka/config.json
20180410_131135/mauka/constants/
20180410_131135/mauka/constants/__init__.py
20180410_131135/mauka/mongo/
20180410_131135/mauka/mongo/mongo.py
20180410_131135/mauka/OpqMauka.py
20180410_131135/mauka/plugins/
20180410_131135/mauka/plugins/AcquisitionTriggerPlugin.py
20180410_131135/mauka/plugins/base.py
20180410_131135/mauka/plugins/broker.py
20180410_131135/mauka/plugins/FrequencyThresholdPlugin.py
20180410_131135/mauka/plugins/history.py
20180410_131135/mauka/plugins/IticPlugin.py
20180410_131135/mauka/plugins/LocalityPlugin.py
20180410_131135/mauka/plugins/manager.py
20180410_131135/mauka/plugins/MeasurementPlugin.py
20180410_131135/mauka/plugins/mock.py
20180410_131135/mauka/plugins/PrintPlugin.py
20180410_131135/mauka/plugins/StatusPlugin.py
20180410_131135/mauka/plugins/ThdPlugin.py
20180410_131135/mauka/plugins/ThresholdPlugin.py
20180410_131135/mauka/plugins/VoltageThresholdPlugin.py
20180410_131135/mauka/plugins/__init__.py
20180410_131135/mauka/protobuf/
20180410_131135/mauka/protobuf/opq.proto
20180410_131135/mauka/protobuf/opq_pb2.py
20180410_131135/mauka/protobuf/util.py
20180410_131135/mauka/protobuf/__init__.py
20180410_131135/mauka/requirements.txt
20180410_131135/scripts/
20180410_131135/scripts/mauka-cli.sh
20180410_131135/scripts/mauka-log.sh
20180410_131135/scripts/mauka-service.sh
+ scp -P 29862 mauka/deploy/20180410_131135.tar.bz2 opquser@emilia.ics.hawaii.edu:/home/opquser/mauka/.
20180410_131135.tar.bz2                                                                                                     100%   22KB  21.6KB/s   00:00
+ rm -rf mauka/deploy/20180410_131135
+ set +x
```
  
Note that *tar.bz2 files in the deploy directory are gitignored.

## 3. Server-side deployment tasks

Now ssh to the server to do the remainder of the deployment:

```
ssh -p 29862 opquser@emilia.ics.hawaii.edu
```

#### 3.1 Unpack tar file with latest release

Change directories into the mauka/ subdirectory, and list the files:

```
opquser@emilia:~/mauka$ ls -al
total 32
drwxr-xr-x  2 opquser opquser  4096 Apr 10 13:19 .
drwxr-xr-x 12 opquser opquser  4096 Apr 10 12:13 ..
-rwxr-xr-x  1 opquser opquser 22143 Apr 10 13:11 20180410_131135.tar.bz2
```

You should see one (or more) timestamped tar.bz2 files (and potentially directories). The most recent timestamped tar.bz2 file is the one you just copied over.  Expand it into a directory as follows:

```
$ tar xf 20180410_131135.tar.bz2
```  

Then cd into that directory, and list the contents:

```
opquser@emilia:~/mauka$ cd 20180410_131135/
opquser@emilia:~/mauka/20180410_131135$ ls -al
total 20
drwxr-xr-x 4 opquser opquser 4096 Apr 10 13:11 .
drwxr-xr-x 3 opquser opquser 4096 Apr 10 13:20 ..
-rwxr-xr-x 1 opquser opquser  874 Apr 10 13:11 deploy-run.sh
drwxr-xr-x 6 opquser opquser 4096 Apr 10 13:11 mauka
drwxr-xr-x 2 opquser opquser 4096 Apr 10 13:11 scripts
opquser@emilia:~/mauka/20180410_131135$
```

#### 3.2 Kill the current OPQMauka process

OPQMauka is installed as a system service which runs under the opq system user account. This is a special account that does not have a login shell which provides hardened security. The other advantage to running as a system service is that the service will automatically boot if the server restarts. Further, the service can be managed by the operating system's `service` command.

To kill the current OPQMauka service, invoke 

`sudo service mauka stop`

#### 3.3 Install the new version of OPQMauka

To install OPQMauka, simple run the `deploy-run.sh` script as root.

```
opquser@emilia:~/mauka/20180410_131135$ sudo ./deploy-run.sh
+ cp scripts/mauka-service.sh /etc/init.d/mauka
+ update-rc.d mauka defaults
+ cp scripts/mauka-cli.sh /usr/local/bin/mauka-cli
+ chmod +x /usr/local/bin/mauka-cli
+ cp scripts/mauka-log.sh /usr/local/bin/mauka-log
+ chmod +x /usr/local/bin/mauka-log
+ mkdir -p /usr/local/bin/opq
+ chown -R opq:opq /usr/local/bin/opq
+ cp -R mauka /usr/local/bin/opq/.
+ cp mauka/config.json /etc/opq/mauka/config.json
+ mkdir -p /var/log/opq
+ chown -R opq:opq /var/log/opq
+ set +o xtrace
```

#### 3.4 Run the new version of OPQMauka

To run the new version of OPQMauka, start the service with 

`sudo service mauka start`

The service will run as a daemon process with all log information going to `/var/log/opq/mauka.log`. This file can be tailed and monitored in real time by running the shortcut `mauka-log`.


## 4. Verify that the new OPQMauka is running

#### 4.1 Check the process list

Check the process list with `ps aux | grep Mauka` and you should see a process for each plugin running under the user `opq`

```
opquser@emilia:~$ ps aux | grep Mauka
opq      14403 10.3  0.5 339040 45704 ?        Sl   13:23   0:41 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14417  0.2  0.4 256992 37744 ?        Sl   13:23   0:00 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14418  0.2  0.4 257128 36880 ?        Sl   13:23   0:01 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14421  0.0  0.4 552088 38660 ?        Sl   13:23   0:00 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14424  0.3  0.4 552108 38804 ?        Sl   13:23   0:01 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14425  0.3  0.4 552116 38812 ?        Sl   13:23   0:01 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14427  0.0  0.4 552140 38660 ?        Sl   13:23   0:00 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14432  0.0  0.4 625888 38832 ?        Sl   13:23   0:00 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opq      14437  0.0  0.4 634104 38776 ?        Sl   13:23   0:00 /usr/bin/python3 /usr/local/bin/opq/mauka/OpqMauka.py /etc/opq/mauka/config.json
opquser  14836  0.0  0.0  12728  2220 pts/3    S+   13:30   0:00 grep Mauka
```

#### 4.2 Check plugin status with mauka-cli

Start the mauka command line interface `mauka-cli`

```
opquser@emilia:~$ mauka-cli
[INFO][2018-04-10 13:32:36,814][14947 manager.py:565 - <module>() ] Starting OpqMauka CLI
[INFO][2018-04-10 13:32:36,814][14947 manager.py:553 - load_config() ] Loading configuration from /etc/opq/mauka/config.json
```


To check the status of the plugins, provide the command `list-plugins`

```
opq-mauka> list-plugins
[DEBUG][2018-04-10 13:33:24,780][14947 manager.py:541 - run_cli() ] name:AcquisitionTriggerPlugin       enabled:Yes process:<Process(Process-8, started)> pid:14437 exit_event:False
name:FrequencyThresholdPlugin       enabled:Yes process:<Process(Process-4, started)> pid:14424 exit_event:False
name:IticPlugin                     enabled:Yes process:<Process(Process-3, started)> pid:14421 exit_event:False
name:StatusPlugin                   enabled:Yes process:<Process(Process-7, started)> pid:14432 exit_event:False
name:ThdPlugin                      enabled:Yes process:<Process(Process-6, started)> pid:14427 exit_event:False
name:VoltageThresholdPlugin         enabled:Yes process:<Process(Process-5, started)> pid:14425 exit_event:False
```

Here, we see that the plugins are enabled, started, and not set to exit which shows they are are in working order.




 
 

