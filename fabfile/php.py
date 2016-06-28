from fabric.api import run


def install_php_fpm():
    run('wget https://templates.wservices.ch/php/init/php-fpm -O ~/init/php-fpm')
    try:
        run('mkdir ~/php')
    except SystemExit:
        pass
    run('wget https://templates.wservices.ch/php/php-fpm.conf -O ~/php/php-fpm.conf')
    run('chmod 755 ~/init/php-fpm')
    run('~/init/php-fpm start')
