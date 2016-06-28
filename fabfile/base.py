import re

from fabric.api import hide, run
from fabric.operations import get
from fabric.contrib.files import append, exists, sed


def get_daemon(initfile):
    """ Parse DAEMON variable in the init file """
    re_daemon = re.compile('^DAEMON=(.+)$', re.MULTILINE)

    if not exists(initfile):
        return None

    local_file = get(initfile)

    f = open(local_file[0], 'r')
    data = f.read()
    f.close()

    match = re_daemon.search(data)
    daemon = ''
    if match:
        daemon = match.group(1)
    if not exists(daemon):
        return None
    return daemon


def load_config(conf_file, base_conf=[], spec_conf=[], delimiter=' '):
    if exists(conf_file):
        with hide('output'):
            config_data = run('cat %s' % conf_file)
    else:
        config_data = ''
    confs = base_conf + spec_conf
    for conf in confs:
        param, value = conf.split(delimiter, 1)
        value = re.sub(r'#.*$', "", str(value)) # Delete comments
        match = re.search('^%s[ ]?%s[ ]?(.*)' % (param, delimiter), config_data, re.MULTILINE)
        if match:
            orig_value = match.group(1).strip()
            orig_line = '%s' % match.group(0).strip()
            if orig_value != str(value):
                if config_data and param in spec_conf:
                    continue # Do not override already existing specific configurations
                print('%s %s change to %s' % (param, orig_value, value))
                sed(conf_file, orig_line, '%s%s%s' % (param, delimiter, value))
            else:
                print('Config OK: %s%s%s' % (param, delimiter, value))
        else:
            print('Add config %s%s%s' % (param, delimiter, value))
            append(conf_file, '%s%s%s' % (param, delimiter, value))


