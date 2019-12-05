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
* apache2
* lighttpd + fastcgi


## Install
Download our fabric package and create a symlink:
```bash
git clone https://github.com/wservices/djangoeurope-fabfile ~/djangoeurope-fabfile
ln -s ~/djangoeurope-fabfile/fabfile ~/fabfile
```


## General advice
For the most installations, you need to create a local port in the djangoeurope control panel first. Make sure that you only open ports which have been added in the control panel. Applications which list on wrong ports are not accessible.
It installs an init script (~/init/appname) to start/stop/restart the application. As an example, you can restart MongoDB by entering '~/init/mongodb restart'.


## Installer
### MongoDB
```bash
fab -H localhost install_mongodb:version="4.2.1",port=(insert the local port number here)
```

Note: The script deletes all existing files in ~/mongodb except of ~/mongodb/data


### Redis
```bash
fab -H localhost install_redis:version='5.0.7',port=(insert the local port number here)
```

Note: The script deletes all existing files in ~/redis except of ~/redis/db


### Elasticsearch
```bash
fab -H localhost install_elasticsearch:version='6.7.0',http_port=(insert the local port number here),transport_port=(insert a 2nd local port number here)
```

Note: The script deletes all existing files in ~/elasticsearch. 1GB RAM and 100 processes (nproc limit) is required. supervisord will be installed and configured in the directory ~/supervisor.


### Jenkins
```bash
fab -H localhost install_jenkins:version='latest',port=(insert the local port number here)
```

Note: The script deletes all existing files in ~/jenkins. 1GB RAM and 100 processes (nproc limit) is required.


### apache2
``` bash
fab -H localhost install_apache2:version='2.4.39',port=(insert the local port number here)
```


### lighttpd
``` bash
fab -H localhost install_lighttpd:port=(insert the local port number here)
```

Note: lighttpd + FastCGI support has been removed in Django 1.9. The installer overrides the files ~/lighttpd/django.conf and ~/lighttpd/port.conf.


### fastcgi
The fastcgi fabric script creates the init script $HOME/init/projectname and configures lighttpd ($HOME/lighttpd/django.conf). The Django project must exists within the directory $HOME/projectname.
``` bash
fab -H localhost install_fastcgi:projectname=(insert the projectname here),hostname=(enter your domain for this Django project)
```

Note: The installer overrides ~/init/projectname with a fastcgi startup script.

