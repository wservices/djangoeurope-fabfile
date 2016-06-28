import os, re

from fabric.api import hide, run, put, prompt
from fabric.operations import get
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed, upload_template

from .base import load_config
from .misc import setup_supervisord


def install_mongodb(*args, **kwargs):
    version = kwargs.get('version') or '3.2.6'
    home = run('echo $HOME')
    port = kwargs.get('port')
    base_dir = kwargs.get('base_dir') or os.path.join(home, 'mongodb')
    data_dir = os.path.join(base_dir, 'data')
    data_backup_dir = os.path.join(home, 'mongodb_data_bak')
    if not port:
        print('Enter a local port for the mongodb server')
        return 1

    if exists(data_dir):
        if exists(data_backup_dir):
            print('Backup directory %s already exists.' % data_backup_dir)
            return 1
        else:
            run('mv %s %s' % (data_dir, data_backup_dir))
    if exists(base_dir):
        run('rm -rf %s' % (base_dir))

    LONG_BIT = run('getconf LONG_BIT')
    if LONG_BIT == '64':
        package_name = 'mongodb-linux-x86_64-%s.tgz' % version
    else:
        package_name = 'mongodb-linux-i686-%s.tgz' % version

    package_path = os.path.join(home, package_name)
    if not exists(package_path):
        with hide('output'):
            run('wget https://fastdl.mongodb.org/linux/%s -O %s' % (package_name, package_path))
    if not exists(package_path.replace('.tgz', '')):
        run('tar xzf ' + package_path)
    run('mv %s %s' % (package_path.replace('.tgz', ''), base_dir))
    if exists(data_backup_dir):
        run('mv %s %s' % (data_backup_dir, data_dir))
    else:
        run('mkdir -p %s/db' % data_dir)

    base_conf = [
        'port = %s' % port,
    ]

    spec_conf = [
        'bind_ip = 127.0.0.1',
        'logappend = True',
        'journal = true',
        'nohttpinterface = true',
    ]

    load_config(
            os.path.join(base_dir, 'mongodb.conf'),
            base_conf=base_conf, spec_conf=spec_conf, delimiter='= '
        )

    if not exists('~/init'):
        run('mkdir ~/init')
    run('wget https://templates.wservices.ch/mongodb/init.%s -O ~/init/mongodb' % LONG_BIT)
    sed('~/init/mongodb', 'DAEMON=/usr/bin/mongod', 'DAEMON=$HOME/mongodb/bin/mongod')
    run('chmod 750 ~/init/mongodb')
    run('~/init/mongodb start')

