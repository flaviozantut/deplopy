from fabric.api import *
from fabric.contrib.project import upload_project
from fabtools import require
from fabtools.files import is_dir
from fabtools.require import nginx, deb, python, files
from fabric.contrib.console import confirm
import fabtools
import os
import uuid
from fabric.colors import red, green
env.hosts = ['vagrant@localhost:2222']
env.passwords = {'vagrant@localhost:2222': 'vagrant'}
remote_dir = '/home/vagrant/project2/'


def  _deb_install_deps():
    # Require some Debian/Ubuntu packages
    fabtools.deb.install([
        'build-essential',
        'python-dev',
        'libxml2-dev',
        'nginx',
        'python-pip',
        'python-virtualenv'
    ])


def  _upload():
     # proj dir create
    # if is_dir(remote_dir) and confirm("proj dir exist! abort ?", default=False):
    #     return

    files.directory(remote_dir, use_sudo=True, owner=env.user, group=env.user, mode='755')

    filename = str(uuid.uuid4())
    local('git archive HEAD | gzip > /tmp/' + filename)
    upload_project(
        local_dir='/tmp/' + filename,
        remote_dir='/tmp/'
    )
    run('tar zxvf /tmp/'+ filename+ ' -C '+ remote_dir)
    local('rm /tmp/' + filename)


def _virtualenv():
    # Require a Python package
    require.python.virtualenv(remote_dir + '.venv')


def _install_requirements():
    with fabtools.python.virtualenv(remote_dir + '.venv'):
            fabtools.python.install_requirements(remote_dir + 'requirements.txt')


def _supervisor():
    # Require a supervisor process for our app
    require.supervisor.process('app',
                               command= remote_dir + '.venv/bin/gunicorn app:app',
                               directory=remote_dir,
                               user=env.user
                               )


def _nginx_proxied_site():
    require.nginx.proxied_site('localhost',
                               docroot=remote_dir + 'public',
                               proxy_url='http://127.0.0.1:8000'
                               )


@task
def setup():
    print(green("Install deb deps"))
    _deb_install_deps()
    print(green("upload project"))
    _upload()
    print(green("Virtual env"))
    _virtualenv()
    print(green("install requirements"))
    _install_requirements()
    print(green("supervisor"))
    _supervisor()
    print(green("nginx proxied site"))
    _nginx_proxied_site()
    print(green("Ok"))



    # # Require an email server
    # require.postfix.server('example.com')

    # # Require a PostgreSQL server
    # require.postgres.server()
    # require.postgres.user('myuser', 's3cr3tp4ssw0rd')
    # require.postgres.database('myappsdb', 'myuser')


    # # Setup a daily cron task
    # fabtools.cron.add_daily('maintenance', 'myuser', 'my_script.py')
