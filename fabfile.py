# -*- coding: utf-8 -*-

import os
import tempfile
import shutil
import errno

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
    'requirements*.in',
    'requirements_*.txt',
    'package.json',
    'npm-shrinkwrap.json',
    'bower.json',
    '/scripts/home_web.static-build.js',
    '/scripts/postactivate',
    '/heating/pilotwire/',
)
EXTCFG_DIR = 'extcfg'
EXTCFG_EXCLUDE = (
    'README',
    'config.yaml',
)
REMOTE_PROJECT_ROOT = '/srv/www/home_web'
REMOTE_VENV_BIN_DIR = '/home/home_web/.virtualenvs/home_web/bin'
PILOTWIRE_PATHS = {
    'local_dir': 'heating/pilotwire/',
    'remote_dir': '/srv/pilotwire',
}
PILOTWIRE_EXCLUDE = (
    '__pycache__/',
    '/__init__.py',
    'test.py',
)

env.colorize_errors = True

fab_roles = {}
try:
    execfile('fab_roles.py', fab_roles)
    env.roledefs = fab_roles['roledefs']
except IOError:
    pass


class TemporaryStaticDir(object):

    SUBDIRS = (
        'src',
        'build',
    )

    def __init__(self):
        self.root_dir = tempfile.mkdtemp()
        os.chmod(self.root_dir, 0o755)
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
    if result:
        abort("Git repository not clean !\n" + result)

def _django_tests():
    local("python manage.py check")
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
    local("node scripts/home_web.static-build.js {}".format(env.static.src_dir))
    shutil.copytree(os.path.join(env.static.src_dir, 'admin'),
                    os.path.join(env.static.build_dir, 'admin'))

@task
@roles('webserver')
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
@roles('webserver')
def deploy_www():
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    _rsync_project(
        remote_dir=':{}/'.format(WWW_RSYNC_MODULE),
        local_dir='./',
        delete=True, exclude=WWW_EXCLUDE,
        extra_opts="--delete-excluded --filter=':- .gitignore'",
    )

@task
@roles('webserver')
def webserver_virtualenv_work():
    with cd(REMOTE_PROJECT_ROOT), \
         settings(sudo_user='home_web'), \
         prefix("source {}".format(
             os.path.join(REMOTE_VENV_BIN_DIR, 'activate'))):
        sudo("pip-sync", pty=False)
        sudo("python manage.py migrate")
        sudo("python manage.py check --deploy")

@task
@roles('webserver')
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
    sudo("kill -HUP $(cat /run/{nginx,supervisord}.pid)")

@task
@roles('pilotwire')
def deploy_pilotwire():
    project.rsync_project(
        exclude=PILOTWIRE_EXCLUDE, delete=True, extra_opts='--delete-excluded',
        **PILOTWIRE_PATHS)
    sudo("kill -HUP $(cat /run/supervisord.pid)")

@task
def coverage():
    try:
        shutil.rmtree('htmlcov')
    except OSError as e:
        if e.errno == errno.ENOENT:
            pass
        else:
            raise
    local("coverage run manage.py test -v2")
    local("coverage html")

@task(default=True)
def deploy():
    _test_repo()
    _django_tests()
    execute(deploy_static)
    execute(deploy_www)
    execute(webserver_virtualenv_work)
    execute(deploy_extcfg)
    execute(deploy_pilotwire)
