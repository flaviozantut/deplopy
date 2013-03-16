from fabric.api import *
from fabric.contrib.project import upload_project
from fabtools import require
import fabtools
import os

env.hosts = ['vagrant@localhost:2222']
env.passwords = {'vagrant@localhost:2222': 'vagrant'}
remote_dir = '/home/vagrant/project/'


def  _deb_install_deps():
    # Require some Debian/Ubuntu packages
    fabtools.deb.install([
        'build-essential',
        'python-dev',
        'libxml2-dev',
        'nginx',
        'python-pip',
        'python-virtualenv'
    ], update=True)


def  _upload():
    upload_project(
        local_dir=os.getcwd(),
        remote_dir=remote_dir
    )


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

    _deb_install_deps()
    _upload()
    _virtualenv()
    _install_requirements()
    _supervisor()
    _nginx_proxied_site()



    # # Require an email server
    # require.postfix.server('example.com')

    # # Require a PostgreSQL server
    # require.postgres.server()
    # require.postgres.user('myuser', 's3cr3tp4ssw0rd')
    # require.postgres.database('myappsdb', 'myuser')


    # # Setup a daily cron task
    # fabtools.cron.add_daily('maintenance', 'myuser', 'my_script.py')
