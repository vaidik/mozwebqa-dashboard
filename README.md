# MozWebQA Dashboard

A little dashboard to keep a track of `skips` and `xfails` in our different
projects

## Basic Usage

### Requirements

This project does not have any major requirements. The only requirement is
`Fabric` if you choose the Fabric way of using this project. Otherwise, you
don't even need that. The other way of using this project is using the Shell
script that does the same thing the Fabric script does.

If you want to go the Fabric way, run:

```
pip install -r requirements.txt
```

### Run It!

```
GH_USER=<Github Username> GH_PASS=<Github Password> fab parse_projects
```

or

```
GH_USER=<Github Username> GH_PASS=<Github Password> ./update.sh <path-to-project-repo>
```

Both the above scripts will clone all the projects in `repos.txt` and try to
parse them using `testsparser.py` and pushes all the important information to
the `gh-pages` branch of any repository so that you can serve this project
using Github Pages.

### Cron Setup

THe ideal setup would be to have the above scripts run via `crontab`. Setup
a cronjob to run the above scripts so that they get executred periodically.
Something like:

```
*/30 * * * * pushd <path to mozwebqa-dashboard> && GH_USER=<Github Username> GH_PASS=<Github Password> fab parse_projects && popd
```

or

```
*/30 * * * * pushd <path to mozwebqa-dashboard> && GH_USER=<Github Username> GH_PASS=<Github Password> ./update.sh . && popd

# or

*/30 * * * * GH_USER=<Github Username> GH_PASS=<Github Password> <path to mozwebqa-dashboard>/update.sh <path to mozwebqa-dashboard>
```

### Adding More Projects

To add a new project to track, add the project's Github repository URL in a
new line in `repos.txt`.
