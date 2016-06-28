import os

from fabric.api import run
from fabric.contrib.files import append, exists


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
        run('wget http://https://templates.wservices.ch/nginx/init -O ~/init/nginx')
        run('chmod 750 ~/init/nginx')

    if exists('~/nginx/nginx.pid'):
        run('~/init/nginx restart')
    else:
        run('~/init/nginx start')
