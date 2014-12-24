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
env.build_dir = None

def _rsync_project(*args, **kwargs):
    """"
    Horrible hack to prevent rsync-project from passing --rsh option to rsync
    """
    bak_any = __builtins__['any']
    __builtins__['any'] = lambda x: False
    out = project.rsync_project(*args, **kwargs)
    __builtins__['any'] = bak_any
    return out

def _filter_output(res, nlines):
    if res.succeeded:
        puts(green('\n'.join(res.split('\n')[-nlines:])))
    else:
        abort(res.stderr)

def _test_repo():
    result = local("git status --porcelain", capture=True)
    if result and not console.confirm("{0} {1}\n{2}".format(
            yellow("Git repository not clean :\n"),
            result,
            yellow("Continue anyway ?"))):
        abort("Abort at user request")

def _build_static():
    with shell_env(DJANGO_CONFIG_PARAM='static_build',
                   DJANGO_STATIC_BUILDDIR=env.build_dir):
        result = local("python manage.py collectstatic --noinput",
                       capture=True)
    _filter_output(result, 1)

def _deploy_static():
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    result = _rsync_project(
        remote_dir=':{}/'.format(env.static_rsync_module),
        local_dir=os.path.join(env.build_dir, ''),
        delete=True, capture=True
    )
    _filter_output(result, 2)

def _deploy_www():
    # Prepend a colon to remote dir to use rsync daemon (host::module/path)
    result = _rsync_project(
        remote_dir=':{}/'.format(env.www_rsync_module),
        local_dir='./',
        delete=True, exclude=env.www_exclude, capture=True,
        extra_opts="--delete-excluded --filter=':- .gitignore'",
    )
    _filter_output(result, 2)

def deploy():
    _test_repo()
    env.build_dir = tempfile.mkdtemp()
    os.chmod(env.build_dir, 0755)
    try:
        with settings(warn_only=True):
            _build_static()
            _deploy_static()
    finally:
        shutil.rmtree(env.build_dir)
    _deploy_www()
