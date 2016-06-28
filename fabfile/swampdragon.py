import os, re

from fabric.api import hide, run, prompt
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed

from .base import get_daemon
from .misc import setup_supervisord
from .redis import install_redis


def install_swampdragon(*args, **kwargs):
    """ Install swampdragon with an example app (todo) """
    home = run('echo $HOME')
    projectname = kwargs.get('project')
    sd_host = kwargs.get('sd_host')
    sd_port = kwargs.get('sd_port')
    redis_port = kwargs.get('redis_port')
    appname = 'todo'
    errors = []

    if not projectname:
        error = 'Enter the project name'
        projectname = prompt(error)
        if not projectname:
            errors.append(error)
    if not sd_host:
        error = 'Enter the domain name of the website'
        sd_host = prompt(error)
        if not sd_host:
            errors.append(error)
            errors.append('Enter the host name which has been used in the django installer name.')
    if not sd_port:
        error = 'Enter a remote port for the swampdragon websocket server'
        sd_port = prompt(error)
        if not sd_port:
            errors.append(error)
    if not redis_port:
        error = 'Enter a local port for the redis server'
        redis_port = prompt(error)
        if not redis_port:
            errors.append(error)

    projectdir = os.path.join(home, projectname)
    if not exists(projectdir):
        errors.append('The Django project ~/%s must already exits.' % projectname)
        errors.append('Swampdragon will be installed into the directory ~/%s.' % projectname)

    init_file = os.path.join(home, 'init', projectname)
    if not exists(init_file):
        errors.append('The gunicorn init file ~/init/%s must exits.' % projectname)

    if errors:
        errors.append('Usage: fab -H localhost install_swampdragon:project=$PROJECT_NAME,sd_host=$SD_HOST,sd_port=$SD_PORT,redis_port=$REDIS_PORT')
        for error in errors:
            print(error)
        return 1

    # Install redis.
    # The redis port is necessary for swampdragon, there is no possibility to connect via unix socket.
    install_redis(port=redis_port)

    # Find already existing virtualenv
    daemon = get_daemon(init_file)
    if not daemon:
        venv_path = prompt('Enter the path to virtualenv (Default: ~/%s/venv/)' % projectname)
        if not venv_path:
            venv_path = os.path.join(projectdir, 'venv')
        if not venv_path.endswith('/'):
            venv_path += '/'
        print('Replace DAEMON variable in init script')
        sed(init_file, 'DAEMON=.*', 'DAEMON=%sbin/gunicorn' % venv_path)
    elif daemon and not daemon.startswith('/usr/bin/'):
        venv_path = os.path.dirname(os.path.dirname(daemon))
        print('Found an existing virtualenv for the project %s in the directory %s' % (projectname, venv_path))
    else:
        print('Replace DAEMON variable in init script')
        sed(init_file, 'DAEMON=/usr/bin/', 'DAEMON=$HOME/%s/venv/bin/' % projectname)
        venv_path = os.path.join(projectdir, 'venv')

    # Replace $HOME and ~, because it doesn't work with supervisord
    venv_path = venv_path.replace('$HOME', home).replace('~', home)
    vpython = os.path.join(venv_path, 'bin', 'python')
    vpip = os.path.join(venv_path, 'bin', 'pip')

    with cd(os.path.join(projectdir)):
        if not exists(os.path.join(venv_path, 'bin', 'python')):
            run('virtualenv %s' % venv_path)
        for packet in ['mysqlclient', 'swampdragon', 'gunicorn==18.0', 'gevent==1.1rc5']:
            if not run(vpip + ' show ' + packet.split('==')[0]):
                with hide('output'):
                    run(vpip + ' install ' + packet)
        if not run(vpip + ' show swampdragon'):
            with hide('output'):
                run(vpip + ' install mysqlclient swampdragon gunicorn==18.0 gevent==1.1rc5')
        if not exists(os.path.join(projectdir, 'todo.tar.gz')):
            run('wget https://templates.wservices.ch/swampdragon/todo.tar.gz -O ~/%s/todo.tar.gz' % projectname)
        if not exists(os.path.join(projectdir, 'todo')):
            run('tar xzf %s/todo.tar.gz' % projectdir)
        sd_settings_file = os.path.join(projectdir, appname, 'swampdragon_settings.py')
        sed(sd_settings_file, 'X_REDIS_PORT', redis_port)
        sed(sd_settings_file, 'X_SD_HOST', sd_host)
        sed(sd_settings_file, 'X_SD_PORT', sd_port)

        settings_file = os.path.join(projectdir, projectname, 'settings.py')
        append(settings_file, 'INSTALLED_APPS = list(INSTALLED_APPS) + [\'swampdragon\', \'todo\']')
        append(settings_file, 'from todo.swampdragon_settings import *')

        urls_file = os.path.join(projectdir, projectname, 'urls.py')
        append(urls_file, 'from django.views.generic import TemplateView')
        append(urls_file, 'urlpatterns += [url(r\'^todo/$\', TemplateView.as_view(template_name=\'index.html\'), name=\'home\')]')

        run(vpython + ' manage.py migrate')
        run(vpython + ' manage.py collectstatic --noinput')

        try:
            run(init_file + ' restart')
        except SystemExit:
            run(init_file + ' start')


        # Setup supervisord
        setup_supervisord()
        runsd_config_file = os.path.join(home, 'supervisor', 'programs', projectname)
        if not exists(runsd_config_file):
            configs = [
                '[program:%s-sd]' % projectname,
                'directory=%s' % projectdir,
                'environment=DJANGO_SETTINGS_MODULE=%s.settings' % projectname,
                'command=%s manage.py runsd' % vpython,
                'stdout_logfile=%s/sd.log' % projectdir,
                'stderr_logfile=%s/sd.err' % projectdir,
                'autostart=true',
                'autorestart=true',
                'stopsignal=INT',
            ]

            for config in configs:
                append(runsd_config_file, config)

            run('~/init/supervisord reload')

