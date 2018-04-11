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

Follow the official instructions for installing the latest version of the 64-bit Linux binaries: https://docs.mongodb.com/manual/tutorial/install-mongodb-on-linux/

If `curl` is not installed, you can install it with 

`sudo apt-get install -y curl`




