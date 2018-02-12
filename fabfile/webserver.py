import os, sys

from fabric.api import run
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed


def install_nginx(*args, **kwargs):
    home = run('echo $HOME')
    nginx_dir = os.path.join(home, 'nginx')
    nginx_port = kwargs.get('port')

    run('mkdir -p %s/conf/sites' % nginx_dir)
    if not exists('%s/conf/nginx.conf' % nginx_dir):
        run('wget https://templates.wservices.ch/nginx/nginx.conf -O %s' % (os.path.join(nginx_dir, 'conf', 'nginx.conf')))
    run('mkdir -p %s/temp' % nginx_dir)
    run('mkdir -p %s/logs' % nginx_dir)

    # save the port number in a separete file in ~/nginx/conf/port
    # This port will be automatically used for future installations
    if nginx_port and not exists(os.path.join(nginx_dir, 'conf', 'port')):
        append(os.path.join(os.path.join(nginx_dir, 'conf', 'port')), str(nginx_port))

    run('mkdir -p ~/init')
    if not exists('~/init/nginx'):
        run('wget https://templates.wservices.ch/nginx/nginx.init -O ~/init/nginx')
        run('chmod 750 ~/init/nginx')

    if exists('~/nginx/nginx.pid'):
        run('~/init/nginx restart')
    else:
        run('~/init/nginx start')


def install_lighttpd(*args, **kwargs):
    home = run('echo $HOME')
    lighttpd_dir = os.path.join(home, 'lighttpd')
    lighttpd_port = kwargs.get('port')

    run('mkdir -p %s' % lighttpd_dir)
    run('wget https://templates.wservices.ch/lighttpd/lighttpd.conf -O %s' % (os.path.join(lighttpd_dir, 'lighttpd.conf')))
    run('wget https://templates.wservices.ch/lighttpd/port.conf -O %s' % (os.path.join(lighttpd_dir, 'port.conf')))
    append(os.path.join(lighttpd_dir, 'port.conf'), 'server.port = %s' % lighttpd_port)
    if not exists(os.path.join(lighttpd_dir, 'django.conf')):
        run('wget https://templates.wservices.ch/lighttpd/django.conf -O %s' % (os.path.join(lighttpd_dir, 'django.conf')))

    run('mkdir -p ~/init')
    if not exists('~/init/lighttpd'):
        run('wget https://templates.wservices.ch/lighttpd/init -O ~/init/lighttpd')
        run('chmod 750 ~/init/lighttpd')

    if exists('~/lighttpd/lighttpd.pid'):
        run('~/init/lighttpd restart')
    else:
        run('~/init/lighttpd start')


def install_apache2(*args,**kwargs):
    PORT = kwargs.get('port')
    version = kwargs.get('version') or '2.4.29'
    home = run('echo $HOME')
    base_dir = os.path.join(home, 'apache2')

    if not PORT:
        print('Enter a local port which has been created in the control panel')
        sys.exit(1)

    if exists(os.path.join(base_dir, 'conf')):
        run('mv %s %s' % (os.path.join(base_dir, 'conf'), '~/apache2_conf_bak'))
    if not exists('httpd-%s.tar.bz2' % version):
        run('wget http://www.us.apache.org/dist//httpd/httpd-%s.tar.bz2 -O httpd-%s.tar.bz2' % (version, version))
    if not exists('httpd-%s' % version):
        run('tar xjf httpd-%s.tar.bz2' % version)
    with cd('httpd-%s' % version):
        if not exists('srclib/apr'):
            run('svn export http://svn.apache.org/repos/asf/apr/apr/trunk srclib/apr')
        run('./buildconf')
        run('./configure --with-ssl=$HOME/openssl/ssl --enable-cgi --enable-so --enable-rewrite --enable-mime-magic --enable-static-rotatelogs --enable-speling --enable-dav-fs --enable-modules=all --enable-modules-shared=all --with-included-apr --prefix=$HOME/apache2 --enable-mpms-shared=all')
        run('make')
        run('make install')

    cmds = [
        'export PATH=$HOME/apache2/bin:$PATH',
        'export LD_LIBRARY_PATH=$HOME/openssl/lib:$HOME/apache2/modules',
        'export LD_RUN_PATH=$HOME/apache2/modules',
    ]
    for cmd in cmds:
        run(cmd)
        append('~/.bashrc', cmd)

    with cd('~/apache2'):
        if exists('conf'):
            run('rm -rf conf')
        if not exists('conf.tar.gz'):
            run('wget https://templates.wservices.ch/apache2/conf.tar.gz -O conf.tar.gz')
        if exists('~/apache2_conf_bak'):
            run('mv %s %s' % ('~/apache2_conf_bak', os.path.join(base_dir, 'conf')))
        else:
            run('tar xzf conf.tar.gz')
            config_files = [
                '~/apache2/bin/apachectl',
                '~/apache2/conf/ports.conf',
                '~/apache2/conf/sites-enabled/000-default.conf',
            ]
            for config_file in config_files:
                sed(config_file, 'HTTP_PORT', PORT)
    sed('~/apache2/bin/apachectl','apache2/bin/envvars' ,'/apache2/conf/envvars')
    if not exists('~/apache2/run'):
        run('mkdir ~/apache2/run')
    if not exists('~/init/apachectl'):
        run('ln -s ~/apache2/bin/apachectl ~/init/apachectl')
    if exists('~/apache2/apche2.pid'):
        run('~/init/apachectl restart')
    else:
        run('~/init/apachectl start')
