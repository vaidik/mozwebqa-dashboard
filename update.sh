#!/bin/bash

# Github Credentials
if [ -z $GH_USER ]; then
    echo "Set environment variable GH_USER to a valid Github username."
    exit 1
fi

if [ -z $GH_PASS ]; then
    echo "Set environment variable GH_PASS to a valid Github account's password."
    exit 1
fi

WORKSPACE_DIR="workspace"
DUMPS_DIR="dumps"
DUMPS_DIR_PATH=$WORKSPACE_DIR/$DUMPS_DIR

# Change directory to project's root
pushd $1

# Create workspace dir if does not exist
if [ ! -d $WORKSPACE_DIR ]; then
    mkdir $WORKSPACE_DIR
fi

# Create dumps dir if does not exist
if [ ! -d $DUMPS_DIR_PATH ]; then
    mkdir $DUMPS_DIR_PATH
fi

# Get project name from repo url
function get_project_name {
    # $1 - the string to perform split on

    index=0
    split_arr[0]=""
    for i in $(echo "$1" | tr "/" " "); do
        split_arr[$index]=$i
        index=$((index+1))
    done

    echo ${split_arr[$((index-1))]}
}

# parse projects
function parse_project {
    repo=$1

    name=`get_project_name $repo`

    pushd $WORKSPACE_DIR
    if [ -d $name ]; then
        pushd $name
        git pull
        popd
    else
        git clone $repo
    fi
    popd

    python testsparser.py $WORKSPACE_DIR/$name > "$DUMPS_DIR_PATH/$name.json"
}

hash jq 2>/dev/null || { echo >&2 "I require jq [http://stedolan.github.io/jq/download/]  but it's not installed.  Aborting."; exit 1; }
for repo in repos=$(cat repos.json | jq '.repos' | tr -d "\""  | tr -d "[,]")
do
    parse_project $repo
done

#This assumes git@github.com:mozilla/mozwebqa-dashboard.git is your origin

git pull origin master
git checkout gh-pages
git rebase master
cp -rvf $DUMPS_DIR_PATH/* $DUMPS_DIR
git add dumps/* && git commit -m "dump on `date`"
git checkout master
git push -f https://$GH_USER:$GH_PASS@github.com/mozilla/mozwebqa-dashboard.git gh-pages

if [ $? -eq 0 ]; then
    RET_VAL=0
else
    RET_VAL=1
fi

echo "PUSHED"

# Go back to the directory you came from
popd

exit $RET_VAL
