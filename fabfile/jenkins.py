import os

from fabric.api import hide, run
from fabric.contrib.files import exists, sed


def install_jenkins(*args, **kwargs):
    home = run('echo $HOME')
    init = os.path.join(home,'init')
    jenkins_base_dir = os.path.join(home, 'jenkins')
    jenkins_init = os.path.join(init, 'jenkins')
    port = kwargs.get('port')
    if not exists(jenkins_base_dir):
        run('mkdir ' + jenkins_base_dir)
    if not exists(os.path.join(jenkins_base_dir, 'jenkins.war')):
        with hide('output'):
            run('wget http://mirrors.jenkins-ci.org/war/latest/jenkins.war -O ~/jenkins/jenkins.war')
    if not exists(os.path.join(jenkins_base_dir, 'org.jenkinsci.main.modules.sshd.SSHD.xml')):
        with hide('output'):
            run('wget https://templates.wservices.ch/jenkins/org.jenkinsci.main.modules.sshd.SSHD.xml -O ~/jenkins/org.jenkinsci.main.modules.sshd.SSHD.xml')
    if not exists(init):
        run('mkdir ~/init')
    if not exists(jenkins_init):
        with hide('output'):
            run('wget https://templates.wservices.ch/jenkins/jenkins.init -O ~/init/jenkins')
        run('chmod 750 ~/init/jenkins')
        sed(jenkins_init, 'PORT=HTTP_PORT', 'PORT=%s' % port)
        run('~/init/jenkins start')
    else:
        run('~/init/jenkins restart')
