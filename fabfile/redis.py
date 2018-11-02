import os, re

from fabric.api import hide, run
from fabric.context_managers import cd
from fabric.contrib.files import append, exists, sed


def redis_status(*args, **kwargs):
    status = run('echo "ping" | redis-cli -s $HOME/redis/redis.sock')
    if status == 'PONG':
        print('Status: OK')
        return 0
    else:
        print('Status: %s' % status)
        return 1


def install_redis(*args, **kwargs):
    port = kwargs.get('port') or 0 # disable TCP port listening by default, use unix sockets (faster).
    home = run('echo $HOME')
    version = kwargs.get('version')
    redis_base_dir = os.path.join(home, 'redis')
    redis_conf_file = os.path.join(redis_base_dir, 'redis.conf')
    redis_conf_order = [
        'dir', 'daemonize', 'bind', 'port', 'logfile', 'pidfile', 'unixsocket', 'unixsocketperm',
        'dbfilename', 'timeout', 'tcp-backlog', 'tcp-keepalive', 'loglevel', 'databases', 'save',
    ]
    redis_base_conf = {
        'dir': redis_base_dir,
        'daemonize': 'yes',
        'logfile': os.path.join(redis_base_dir, 'redis.log'),
        'pidfile': os.path.join(redis_base_dir, 'redis.pid'),
        'unixsocket': os.path.join(redis_base_dir, 'redis.sock'),
        'unixsocketperm': 700,
    }
    redis_spec_conf = {
        'bind': '127.0.0.1',
        'dbfilename': 'dump.rdb',
        'timeout': 0,
        'tcp-backlog': 511,
        'tcp-keepalive': 60,
        'loglevel': 'notice',
        'databases': 16,
        'save': '900 1 300 10 60 10000',
    }

    if port:
        redis_base_conf['port'] = port
    else:
        redis_spec_conf['port'] = port

    redis_conf = redis_base_conf
    redis_conf.update(redis_spec_conf)

    restart = False

    if not exists(redis_base_dir):
        run('mkdir ' + redis_base_dir)

    if version:
        run('wget http://download.redis.io/releases/redis-{0}.tar.gz -O redis-{0}.tar.gz'.format(version))
        run('tar xzf redis-{0}.tar.gz'.format(version))
        with cd(os.path.join(home, 'redis-{0}'.format(version))):
            run('make')
            run('make PREFIX={0} install'.format(redis_base_dir))

    if exists(redis_conf_file):
        restart = True
        with hide('output'):
            redis_config_data = run('cat %s' % redis_conf_file)
    else:
        redis_config_data = ''

    for param in redis_conf_order:
        value = redis_conf.get(param)
        value = re.sub(r'#.*$', "", str(value)) # Delete comments
        match = re.search('^%s +(.*)' % param, redis_config_data, re.MULTILINE)
        if match:
            orig_value = match.group(1).strip()
            orig_line = '%s' % match.group(0).strip()
            if orig_value != str(value):
                if redis_config_data and param in redis_spec_conf.keys():
                    continue # Do not override already existing specific configurations
                print('%s %s change to %s' % (param, orig_value, value))
                print('group 0: %s' % orig_line)
                sed(redis_conf_file, orig_line, '%s %s' % (param, value), backup='')
            else:
                print('Config OK: %s %s' % (param, value))
        else:
            print('Add config %s %s' % (param, value))
            append(redis_conf_file, '%s %s' % (param, value))

    with hide('output'):
        run('wget https://templates.wservices.ch/redis/redis-server -O ~/init/redis-server')
        run('chmod 755 ~/init/redis-server')

    if version:
        sed('~/init/redis-server', 'DAEMON=/usr/bin/redis-server', 'DAEMON=$HOME/redis/bin/redis-server', backup='')

    if restart:
        run('~/init/redis-server restart')
    else:
        run('~/init/redis-server start')
    return redis_status()
