# Installing MongoDB

The OPQ system uses [MongoDB](https://www.mongodb.com/) for storage and management of data. In order for OPQView reactive (real-time) queries to be performant in a production environment, Mongo must be configured with replication sets and oplog tailing. This guide provides information for installing a MongoDB server with multiple replica sets configured to allowed oplog tailing.

## 1. Prelude: account setup

Here are one-time configuration activities required to perform an installation of MongoDB.

#### 1.1 Obtain the opquser account credentials

MongoDB is installed using the opquser account.  You need to obtain the password for opquser in order to do this deployment.

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

## 1. Installing MongoDB

Copy the `install-mongod.sh` script found in the `opq/util/mongod/install` directory to the server you wish to install it on.

As root, run the install script.

```
$ sudo ./install-mongodb.sh 
+ apt-get install -y curl
Reading package lists... Done
Building dependency tree       
Reading state information... Done
curl is already the newest version (7.52.1-5+deb9u5).
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
+ DIST=mongodb-linux-x86_64-3.6.3
+ curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-3.6.3.tgz
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 82.8M  100 82.8M    0     0  13.3M      0  0:00:06  0:00:06 --:--:-- 19.3M
+ tar xvf mongodb-linux-x86_64-3.6.3.tgz
mongodb-linux-x86_64-3.6.3/README
mongodb-linux-x86_64-3.6.3/THIRD-PARTY-NOTICES
mongodb-linux-x86_64-3.6.3/MPL-2
mongodb-linux-x86_64-3.6.3/GNU-AGPL-3.0
mongodb-linux-x86_64-3.6.3/bin/mongodump
mongodb-linux-x86_64-3.6.3/bin/mongorestore
mongodb-linux-x86_64-3.6.3/bin/mongoexport
mongodb-linux-x86_64-3.6.3/bin/mongoimport
mongodb-linux-x86_64-3.6.3/bin/mongostat
mongodb-linux-x86_64-3.6.3/bin/mongotop
mongodb-linux-x86_64-3.6.3/bin/bsondump
mongodb-linux-x86_64-3.6.3/bin/mongofiles
mongodb-linux-x86_64-3.6.3/bin/mongoreplay
mongodb-linux-x86_64-3.6.3/bin/mongoperf
mongodb-linux-x86_64-3.6.3/bin/mongod
mongodb-linux-x86_64-3.6.3/bin/mongos
mongodb-linux-x86_64-3.6.3/bin/mongo
mongodb-linux-x86_64-3.6.3/bin/install_compass
+ INSTALL_DIR=/usr/local/bin/mongodb
+ mkdir -p /usr/local/bin/mongodb
+ cp -R -n mongodb-linux-x86_64-3.6.3/bin mongodb-linux-x86_64-3.6.3/GNU-AGPL-3.0 mongodb-linux-x86_64-3.6.3/MPL-2 mongodb-linux-x86_64-3.6.3/README mongodb-linux-x86_64-3.6.3/THIRD-PARTY-NOTICES /usr/local/bin/mongodb
+ mkdir -p /var/log/mongodb
+ chown -R opq:opq /var/log/mongodb
+ echo 'export PATH=/usr/local/bin/mongodb/bin:$PATH'
+ DB_BASE=/var/mongodb/opq
+ mkdir -p /var/mongodb/opq/rs0
+ mkdir -p /var/mongodb/opq/rs1
+ mkdir -p /var/mongodb/opq/rs2
+ chown -R opq:opq /var/mongodb/opq
+ echo 'If you want mongo on your path, reload with ". ~/.profile"'
If you want mongo on your path, reload with ". ~/.profile"
+ set +x
```

The script works by performing the following steps:

1. Ensure curl is installed using system package manager
2. Download latest generic mongodb community server using curl
3. Installs mongodb under /usr/local/bin/mongodb
4. Creates data directories at /var/mongodb/opq/rs[0-2]
5. Create log directory at /var/log/mongodb
6. Set's ownership of data and log dirs to the system level `opq` user

## 2. Installing the MongoDB service

This step will install MongoDB as a system level service. This allows MongoDB to be managed by the service daemon and to autostart when the server starts. This step requires three scripts:

1. `opq/util/mongod/install/install-service.sh`: Installs the service file, runs script, and updates the service daemon
2. `opq/util/mongod/install/mongod-service.sh`: The actual unit file that init.d/systemd uses to run mongod as a service
3. `opq/util/mongod/install/start-mongod.sh`: The run script that the service uses to start multiple replica sets

#### 2.1 Copy service scripts to server

First, copy all three scripts to the server that you wish to setup the mongod service. You may use the opquser account to do this. Ensure that all three scripts are siblings in the same directory.

#### 2.2 Run the install-service.sh script

As root, run install-service.sh

```
$ sudo ./install-service.sh 
+ cp start-mongod.sh /usr/local/bin/mongodb/.
+ chown opq:opq /usr/local/bin/mongodb/start-mongod.sh
+ chmod +x /usr/local/bin/mongodb/start-mongod.sh
+ cp mongod-service.sh /etc/init.d/mongod
+ chown opq:opq /etc/init.d/mongod
+ chmod +x /etc/init.d/mongod
+ update-rc.d mongod defaults
+ set +x
```

#### 2.3 Start the mongod service

As root, you should now be able to run the mongod service using `/etc/init.d/mongod start`.

```
sudo /etc/init.d/mongod start
[ ok ] Starting mongod (via systemctl): mongod.service.
```

Please note that as a system service, mongod will also start automatically any time the server is restarted.

To verify that mongod is running with three replica sets, we can look at the process table and select those with mongod in the name.

```
$ ps aux | grep mongod
opq        673  0.2  1.3 1005344 55680 ?       Sl   08:18   0:01 opq       2545 12.8  1.3 1005348 55996 ?       Sl   09:39   0:00 /usr/local/bin/mongodb/bin/mongod --replSet opqrs --port 27018 --dbpath /var/mongodb/opq/rs0 --fork --logpath /var/log/mongodb/rs0.loq
                                                                 opq       2586 15.0  1.3 1005348 55228 ?       Sl   09:39   0:00 /usr/local/bin/mongodb/bin/mongod --replSet opqrs --port 27019 --dbpath /var/mongodb/opq/rs1 --fork --logpath /var/log/mongodb/rs1.loq
                                                                 opq       2618 19.0  1.3 1005348 55280 ?       Sl   09:39   0:00 /usr/local/bin/mongodb/bin/mongod --replSet opqrs --port 27020 --dbpath /var/mongodb/opq/rs2 --fork --logpath /var/log/mongodb/rs2.loq

```

Here we see three mongod processes each running on a different port, each with their oen data directory, and each with their own log file.

At this point in time, it should also be possible to connect to the server from opquser using the mongo command (assuming you've added the mongodb binary to your PATH).

```
$ mongo --port 27018
MongoDB shell version v3.6.3
connecting to: mongodb://127.0.0.1:27018/
MongoDB server version: 3.6.3
Welcome to the MongoDB shell.
For interactive help, type "help".
For more comprehensive documentation, see
	http://docs.mongodb.org/
Questions? Try the support group
	http://groups.google.com/group/mongodb-user
Server has startup warnings: 
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] 
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] ** WARNING: Using the XFS filesystem is strongly recommended with the WiredTiger storage engine
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] **          See http://dochub.mongodb.org/core/prodnotes-filesystem
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] ** WARNING: Access control is not enabled for the database.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Read and write access to data and configuration is unrestricted.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] ** WARNING: This server is bound to localhost.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Remote systems will be unable to connect to this server. 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Start the server with --bind_ip <address> to specify which IP 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          addresses it should serve responses from, or with --bind_ip_all to
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          bind to all interfaces. If this behavior is desired, start the
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          server with --bind_ip 127.0.0.1 to disable this warning.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
```

You may see some warnings that we can ignore for the time being, but you can also verify that you can connect to the running mongod instance using this approach.

## 3. Configuring mongod to support oplog

First, connect to the primary mongod instance

```
$ mongo --port 27018
MongoDB shell version v3.6.3
connecting to: mongodb://127.0.0.1:27018/
MongoDB server version: 3.6.3
Server has startup warnings: 
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] 
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] ** WARNING: Using the XFS filesystem is strongly recommended with the WiredTiger storage engine
2018-04-11T08:18:04.158-1000 I STORAGE  [initandlisten] **          See http://dochub.mongodb.org/core/prodnotes-filesystem
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] ** WARNING: Access control is not enabled for the database.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Read and write access to data and configuration is unrestricted.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] ** WARNING: This server is bound to localhost.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Remote systems will be unable to connect to this server. 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          Start the server with --bind_ip <address> to specify which IP 
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          addresses it should serve responses from, or with --bind_ip_all to
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          bind to all interfaces. If this behavior is desired, start the
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] **          server with --bind_ip 127.0.0.1 to disable this warning.
2018-04-11T08:18:05.062-1000 I CONTROL  [initandlisten] 
> 
```

Once connected, we can now configure the replica sets. We will first create a config variable:

```
config = {_id: "opqrs", members: [{_id: 0, host: "localhost:27018"}, {_id: 1, host: "localhost:27019"},{_id: 2, host: "localhost:27020"}]};
```

Next, we will initiate the replica set with the config that we just created using `rs.initiate(config);`

```
> rs.initiate(config);
{
	"ok" : 1,
	"operationTime" : Timestamp(1523475887, 1),
	"$clusterTime" : {
		"clusterTime" : Timestamp(1523475887, 1),
		"signature" : {
			"hash" : BinData(0,"AAAAAAAAAAAAAAAAAAAAAAAAAAA="),
			"keyId" : NumberLong(0)
		}
	}
}
```

At this point, you should be ready to go. See the official mongodb documentation if you wish to setup further access rights such as users or permissions.