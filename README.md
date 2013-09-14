# MozWebQA Dashboard

A little dashboard to keep a track of `skips` and `xfails` in our different
projects

## Basic Usage

### Install Requirements

```
pip install -r requirements.txt
```

### Run It!

```
GH_USER=<Github username> GH_PASS=<Github password> fab parse_projects
```

or

```
GH_USER=<Github username> GH_PASS=<Github password> ./update.sh .
```

Both the above scripts will clone all the projects in `repos.txt` and try to
parse them using `testsparser.py` and pushes all the important information to
the `gh-pages` branch of any repository so that you can serve this project
using Github Pages.

### Cron Setup

THe ideal setup would be to have the above scripts run using `crontab`. Setup
a cronjob to run the above scripts so that they get executred periodically.
