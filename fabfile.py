# -*- coding: utf-8 -*-

import os
import tempfile
import shutil

from fabric.api import *
from fabric.colors import green, yellow
from fabric.contrib import console, project

env.colorize_errors = True
env.static_rsync_module = 'home_web-static'
env.www_rsync_module = 'home_web-www'
env.www_exclude = [
    '.git/',
    '.gitignore',
    '/extcfg/',
    '/fabfile.py',
    '/requirements_dev.txt',
    '/tmp/',
    'static/',
]

class TemporaryStaticDir(object):

    SUBDIRS = (
        'src',
        'build',
    )
    TOOLS_DIR = './tools'

    def __init__(self):
        self.root_dir = tempfile.mkdtemp()
        os.chmod(self.root_dir, 0755)
        shutil.copytree(self.TOOLS_DIR, self.tools_dir)
        for sd in self.SUBDIRS:
            os.mkdir(os.path.join(self.root_dir, sd))

    def __getattr__(self, name):
        if not (self.root_dir and name.endswith('_dir')):
            raise AttributeError("'{}' object has no attribute '{}'".format(
                self.__class__.__name__, name
            ))
        return os.path.join(self.root_dir, name[:-4])

    def delete(self):
        shutil.rmtree(self.root_dir)
        self.root_dir = None

def _test_repo():
    result = local("git status --porcelain", capture=True)
    if result and not console.confirm("{0} {1}\n{2}".format(
            yellow("Git repository not clean :\n"),
            result,
            yellow("Continue anyway ?"))):
        abort("Abort at user request")

@task
def collect_static():
    env.static = TemporaryStaticDir()
    with shell_env(DJANGO_CONFIG_PARAM='static_build',
                   DJANGO_STATIC_BUILDDIR=env.static.src_dir):
        local("python manage.py collectstatic --noinput")

@task
def build_static():
    collect_static()
    with lcd(env.static.tools_dir):
        local("node r.js -o app.build.js appDir={0} dir={1}".format(
            os.path.relpath(env.static.src_dir, env.static.tools_dir),
            os.path.relpath(env.static.build_dir, env.static.tools_dir)
        ))

@task
def deploy_static():
    build_static()
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    project.rsync_project(
        remote_dir=':{}/'.format(env.static_rsync_module),
        local_dir=os.path.join(env.static.build_dir, ''),
        delete=True
    )
    env.static.delete()

@task
def deploy_www():
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    project.rsync_project(
        remote_dir=':{}/'.format(env.www_rsync_module),
        local_dir='./',
        delete=True, exclude=env.www_exclude,
        extra_opts="--delete-excluded --filter=':- .gitignore'",
    )

@task(default=True)
def deploy():
    _test_repo()
    deploy_static()
    deploy_www()
