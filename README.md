# djangoeurope fabfile

## What is fabric and fabfile and for what I can use it?
Fabric is a Python library and command-line tool for streamlining the use of SSH for application deployment. 
A fabfile is what controls what Fabric executes.
We created some fabfiles (fabric scripts) which makes it easier to install packages on djangoeurope servers.

Available installers

* MongoDB
* Redis
* Elasticsearch
* Jenkins
* Swamdragon


## Install
Download our fabric package in the directory ~/fabric.
Run the following command to download and update ~/fabfile (last update: 25.05.2016).
``` bash
wget -O - https://templates.wservices.ch/install_fab_packages.sh | sh
```

Or download from git repository
``` bash
git clone https://github.com/wservices/djangoeurope-fabfile ~/djangoeurope-fabfile
ln -s ~/djangoeurope-fabfile/fabfile ~/fabfile
```


## General advice
For the most installations you need to create a local port in the djangoeurope control panel first. Make sure that you only open ports which has been added in the control panel. Applications which list on wrong ports will not be accessible.


## Installer
### MongoDB
    fab -H localhost install_mongodb:version="3.2.8",port=(insert the local port number here)

Note: The script deletes all existing files in ~/mongodb except of ~/mongodb/data


### Redis
    fab -H localhost install_redis:version='3.2.3',port=(insert the local port number here)

Note: The script deletes all existing files in ~/redis except of ~/redis/db


### Elasticsearch
    fab -H localhost install_elasticsearch:version='2.3.5',port=(insert the local port number here)

Note: The script deletes all existing files in ~/elasticsearch. To run elasticsearch the Premium plan is required.


### Jenkins
    fab -H localhost install_jenkins:version='latest',port=(insert the local port number here)

Note: The script deletes all existing files in ~/jenkins. The Premium plan is required.


### Swampdragon
The swampdragon fabric script installs swampdragon with the tutorial 1 of the official swampdragon page. Before running this script, run the Django one click installer in the control panel.
To set basic configuration parameters, enter the following commands and replace the values of the variables.
``` bash
export PROJECT_NAME=(enter the name of your project here)
export SD_HOST=(enter the domain name of the website)
export SD_PORT=(enter the remote port)
export REDIS_PORT=(enter the local port of redis)
```

Run the fabric script
``` bash
fab -H localhost install_swampdragon:project=$PROJECT_NAME,sd_host=$SD_HOST,sd_port=$SD_PORT,redis_port=$REDIS_PORT
```

Note: The development of the swampdragon project is currently on hold.
