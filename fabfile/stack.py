import os

from fabric.api import run
from fabric.contrib.files import exists, sed

from webserver import install_lighttpd


def install_fastcgi(*args, **kwargs):
    home = run('echo $HOME')
    projectname = kwargs.get('projectname', 'mydomain.com')
    hostname = kwargs.get('hostname', 'mysite_project')
    project_dir = os.path.join(home, projectname)
    lighttpd_dir = os.path.join(home, 'lighttpd')
    init_file = os.path.join(home, 'init', projectname)

    # Check if lighttpd exists
    if not exists(lighttpd_dir):
        port = kwargs.get('port')
        if not port:
            print('The directory %s does not exists. Install lighttpd...' % lighttpd_dir)
            port = int(input('Enter the local port number for lighttpd: '))
        install_lighttpd(port=port)

    # Append configuration in file ~/lighttpd/django.conf
    django_conf = os.path.join(lighttpd_dir, 'django.conf')
    django_conf_new = os.path.join(lighttpd_dir, 'django.conf.new')
    run('wget https://templates.wservices.ch/fastcgi/django.conf -O %s' % django_conf_new)
    sed(django_conf_new, 'projectname', projectname)
    sed(django_conf_new, 'hostname', hostname.replace('.', '\\.'))
    run('cat {0} >> {1} && rm {0}'.format(django_conf_new, django_conf))
    run('~/init/lighttpd restart')

    # Create fastcgi init script
    run('wget https://templates.wservices.ch/fastcgi/init -O %s' % init_file)
    sed(init_file, 'projectname', projectname)
    run('chmod 750 %s' % init_file)
    run('%s restart' % init_file)

