# Configure the host

This chapter documents packages that must be installed in order to deploy OPQ Cloud-based services. These instructions are currently specific to ITS hosts. 

## Install Linux

(Indicate what version of Linux we are using, and pointers to directions on how to install on ITS hosts.)

## Create system and user-level accounts 

Create a system account called 'opq' that does not have login privileges. For example,

```
(command to create opq system account)
```

Create a second account called 'opquser' with normal user privileges. For example,

```
(command to create opquser account)
```

For opquser account, create the top-level directories: mauka, makai, view, health, and mongodb.  Deployment scripts and files for each service will be located and maintained within these directories

## Install git

## Install apache

## Install mongo

## Install node
