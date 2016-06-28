import os, re

from fabric.api import run
from fabric.context_managers import cd
from fabric.contrib.files import exists


def install_openssl(*args,**kwargs):
    version = kwargs.get('version') or '1.0.2h'
    package_name='openssl-%s' % version

    if not exists(package_name + '.tar.gz'):
        run('wget https://www.openssl.org/source/openssl-%s.tar.gz -O %s.tar.gz' % (version, package_name))
    if not exists(package_name):
        run('tar xzf %s.tar.gz' % package_name)
    with cd(package_name):
        run('./Configure --prefix=$HOME/openssl shared linux-generic32')
        run('make')
        run('make install')


def setup_supervisord(*args, **kwargs):
    run('mkdir -p ~/supervisor/programs')
    run('wget https://templates.wservices.ch/supervisor/supervisord.conf -O ~/supervisor/supervisord.conf')
    run('wget https://templates.wservices.ch/supervisor/init -O ~/init/supervisord')
    run('chmod 700 ~/init/supervisord')
    try:
        run('~/init/supervisord start')
    except SystemExit:
        run('~/init/supervisord restart')

