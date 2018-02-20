# OPQBox Updater Installation

Code for the box updater can be found [here](https://github.com/openpowerquality/opq/tree/master/box/Software/Updater).

### Summary
The OPQBox updater provides a way to securely and remotely update any OPQBox. The updater is installed on every box upon setup. Along with the updater installation, a cronjob is setup to run the updater once a day to check for a new update package from emilia.

#### The update process
1. Download the version file (version.json, contains latest update package info) from an OPQ server
2. Compare the downloaded version file to the boxes local version file
3. Download the public key, update package, and signature from the OPQ server
4. Verify the update package against the public key and signature
5. Unzip the update package
6. Run the updater script file

#### Installation
* Run setup with -> python3 setup.py install
  * Installs updater's python dependencies
  * Installs box_updater.py to /usr/local/bin/box_updater.py
  * Installs configuration file, updater_config.json, to /etc/opq/updater_config.json
  * Sets up the cronjob to call the updater once a day
* Install cron job -> python3 setup_cron.py
  * Sets a cronjob to run the updater once a day
* DONE

#### File Notes
1. box_updater.py
  * Contains the main method to run an update
2. updater_config.json
  * Specifies the download path for update package's files
    * i.e. The version file, public key, update package, and signature are downloaded to this directory on the box
  * Specifies the url for an OPQ server that holds the update package
  * Specifies the name of the version file to be grabbed from and OPQ server
3. setup.py
  * The setup script to install the updater and its dependencies
4. setup_cron.py
  * Script to setup the updater cronjob

#### Troubleshooting
* The updater logs all its updates and errors in /var/log/opq/box_updater.log
  * The cronjob sets this up by piping the updaters output stream (&>> /var/log/opq/box_updater.log)
