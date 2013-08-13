import json
import os

from datetime import datetime
from fabric.api import lcd
from fabric.api import local
from fabric.api import run
from fabric.api import settings

DUMPS_DIR = 'dumps'
WORKSPACE_DIR = 'workspace'


def parse_projects():
    repos = json.loads(open('config.json').read())
    repos = repos['repos']

    if not os.path.exists(WORKSPACE_DIR):
        local('mkdir %s' % WORKSPACE_DIR)

    if not os.path.exists(os.path.join(WORKSPACE_DIR, DUMPS_DIR)):
        local('mkdir %s' % os.path.join(WORKSPACE_DIR, DUMPS_DIR))

    for repo in repos:
        name = repo.split('/')[-1].split('.')[0]
        path = os.path.join(WORKSPACE_DIR, name)
        with lcd(WORKSPACE_DIR):
            if os.path.exists(path):
                with lcd(name):
                    local('git pull')
            else:
                local('git clone %s' % repo)
        local('python testsparser.py %s > %s.json' % (path,
                                                      os.path.join(WORKSPACE_DIR, DUMPS_DIR, name)))

    local("git checkout gh-pages")
    local("git rebase master")
    with settings(warn_only=True):
        local("cp -rvf %s/* %s" % (os.path.join(WORKSPACE_DIR, DUMPS_DIR), DUMPS_DIR))
        local("git add dumps/* && git commit -m \'dump on %s\'" % datetime.now().strftime("%B %d, %Y at %H:%M:%S"))
        local("git checkout master")
    local("git push -f origin gh-pages")
