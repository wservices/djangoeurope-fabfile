import os, re

from fabric.api import hide, run, put, prompt
from fabric.operations import get
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed, upload_template

from .base import load_config
from .misc import setup_supervisord


def install_elasticsearch(*args, **kwargs):
    VERSION = kwargs.get('version', '6.4.1')
    http_port = kwargs.get('http_port')
    if not http_port:
        print('Enter a local http port for the elasticsearch server')
        return 1
    transport_port = kwargs.get('transport_port')
    if not transport_port:
        print('Enter a local transport port for the elasticsearch server')
        return 1
    if not exists('elasticsearch-%s.tar.gz' % VERSION):
        with hide('output'):
            run('wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-%s.tar.gz' % VERSION)
    if exists('elasticsearch'):
        if exists('supervisor'):
            with cd('supervisor'):
                try:
                    run('supervisorctl stop elasticsearch')
                except SystemExit:
                    pass
        if exists('elasticsearch/data'):
            run('mv elasticsearch/data elasticsearch_data_bak')
        if exists('elasticsearch/config'):
            run('mv elasticsearch/config elasticsearch_conf_bak')
        run('rm -rf elasticsearch')

    run('tar xzf elasticsearch-%s.tar.gz' % VERSION)
    run('mv elasticsearch-%s elasticsearch' % VERSION)

    for bak,dst in {
            'elasticsearch_data_bak': 'elasticsearch/data',
            'elasticsearch_conf_bak': 'elasticsearch/config',
        }.items():
        if exists(bak):
            if exists(dst):
                run('rm -rf %s' % dst)
            run('mv %s %s' % (bak, dst))

    home = run('echo $HOME')
    base_dir = os.path.join(home, 'elasticsearch')
    base_conf = [
        'http.port: %s' % http_port,
        'transport.tcp.port: %s' % transport_port,
    ]
    spec_conf = [
        'network.host: 127.0.0.1',
        #'node.local: True',
        #'index.number_of_shards: 1',
        #'index.number_of_replicas: 0',
    ]

    load_config(
            os.path.join(base_dir, 'config', 'elasticsearch.yml'),
            base_conf=base_conf, spec_conf=spec_conf, delimiter=': '
        )

    setup_supervisord()
    runsd_config_file = os.path.join(home, 'supervisor', 'programs', 'elasticsearch')

    if not exists(runsd_config_file):
        append(runsd_config_file, '[program:elasticsearch]')

    configs = [
        'directory=%s' % base_dir,
        'environment=MALLOC_ARENA_MAX="4",ES_HEAP_SIZE="300M",JAVA_OPTS="-XX:ParallelGCThreads=1 -XX:ReservedCodeCacheSize=8m -XX:MaxPermSize=64m"',
        'command=%s/bin/elasticsearch' % base_dir,
        'stdout_logfile=%s/sd.log' % base_dir,
        'stderr_logfile=%s/sd.err' % base_dir,
        'autostart=true',
        'autorestart=true',
        'stopsignal=INT',
    ]

    load_config(runsd_config_file, base_conf=configs, delimiter='=')

    run('~/init/supervisord reload')


