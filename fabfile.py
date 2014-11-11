# -*- coding: utf-8 -*-

from fabric.api import *

env.remote_root = '/srv/www/home_web'

def push():
    local("git commit --patch")
    local("git push")

def remote_deploy():
    with cd(env.remote_root):
        with settings(sudo_user='home_web'):
            sudo("git pull")
            with prefix("source ~/.virtualenvs/home_web/bin/activate"):
                sudo("python manage.py collectstatic --noinput --clear")

def deploy():
    push()
    remote_deploy()
