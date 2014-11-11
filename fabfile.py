# -*- coding: utf-8 -*-

from fabric.api import *

env.remote_root = '/srv/www/home_web'

def push():
    local("git commit --patch")
    local("git push")

def remote_deploy():
    pyvenv = '~/.virtualenvs/home_web/bin/python'
    with cd(env.remote_root):
        with settings(sudo_user='home_web'):
            sudo("git pull")
            sudo(pyvenv + " manage.py collectstatic --noinput --clear")

def deploy():
    push()
    remote_deploy()
