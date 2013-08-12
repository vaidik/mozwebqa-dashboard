import os

from datetime import datetime
from fabric.api import lcd
from fabric.api import local
from fabric.api import run

WORKSPACE_DIR = 'workspace'

repos = [
    'git@github.com:mozilla/marketplace-tests.git',
]


def prepare_deploy():
    if not os.path.exists('workspace'):
        local('mkdir workspace')

    for repo in repos:
        name = repo.split('/')[-1].split('.')[0]
        path = os.path.join(WORKSPACE_DIR, name)
        with lcd(WORKSPACE_DIR):
            if os.path.exists(path):
                with lcd(name):
                    local('git pull')
            else:
                local('git clone %s' % repo)
        local('python testparser.py %s > dumps/%s.json' % (path, name))
    local("git add dumps/* && git commit -m \'dump on %s\'" % datetime.now().strftime("%B %d, %Y at %H:%M:%S"))
    local("git push")
