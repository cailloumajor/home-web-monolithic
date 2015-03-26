# -*- coding: utf-8 -*-

import os
import tempfile
import shutil

from fabric.api import *
from fabric.colors import green, yellow
from fabric.contrib import console, project

STATIC_RSYNC_MODULE = 'home_web-static'
WWW_RSYNC_MODULE = 'home_web-www'
WWW_EXCLUDE = (
    '.git/',
    '.gitignore',
    '/extcfg/',
    '/fabfile.py',
    '/requirements_dev.txt',
    '/tmp/',
    'static/',
    '.coveragerc',
    'tests/',
)
EXTCFG_DIR = 'extcfg'
EXTCFG_EXCLUDE = (
    'README',
    'config.yaml',
)

env.colorize_errors = True
try:
    with open('fab_hosts', 'r') as f:
        env.hosts = f.read().splitlines()
except IOError:
    pass

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

def _rsync_project(*args, **kwargs):
    """"
    Horrible hack to prevent rsync-project from passing --rsh option to rsync
    """
    bak_any = __builtins__['any']
    __builtins__['any'] = lambda x: False
    out = project.rsync_project(*args, **kwargs)
    __builtins__['any'] = bak_any
    return out

def _test_repo():
    if local("git symbolic-ref --short -q HEAD", capture=True) != 'master':
        abort("Not on 'master' branch !")
    result = local("git status --porcelain", capture=True)
    if result and not console.confirm("{0} {1}\n{2}".format(
            yellow("Git repository not clean :\n"),
            result,
            yellow("Continue anyway ?"))):
        abort("Abort at user request")

def _django_tests():
    local("python -Wall manage.py test")

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
    _rsync_project(
        remote_dir=':{}/'.format(STATIC_RSYNC_MODULE),
        local_dir=os.path.join(env.static.build_dir, ''),
        delete=True
    )
    env.static.delete()

@task
def deploy_www():
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    _rsync_project(
        remote_dir=':{}/'.format(WWW_RSYNC_MODULE),
        local_dir='./',
        delete=True, exclude=WWW_EXCLUDE,
        extra_opts="--delete-excluded --filter=':- .gitignore'",
    )

@task
def coverage():
    shutil.rmtree('htmlcov')
    local("coverage run manage.py test -v2")
    local("coverage html")

@task(default=True)
def deploy():
    _test_repo()
    _django_tests()
    deploy_static()
    deploy_www()

@task
def deploy_extcfg():
    _test_repo()
    paths = [
        os.path.join(os.path.relpath(dp, EXTCFG_DIR), f)
        for dp, dn, fn in os.walk(EXTCFG_DIR)
        for f in fn if f not in EXTCFG_EXCLUDE
    ]
    project.rsync_project(remote_dir='', local_dir=EXTCFG_DIR, delete=True)
    with cd(EXTCFG_DIR):
        for path in paths:
            sudo("cp {src} {dst}".format(
                src=path, dst=os.path.join(os.sep, path)
            ))
    sudo("kill -HUP $(cat /run/nginx.pid)")
    sudo("kill -HUP $(cat /run/supervisord.pid)")
