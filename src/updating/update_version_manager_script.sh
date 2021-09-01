#!/bin/bash
home_dir="/home/pi/"
version_manager_path="${home_dir}smartbench-version-manager/"
version_manager_main="${home_dir}smartbench-version-manager/src/version_manager_main.py"

# kill existing update process
killall python
sleep 5
cd version_manager_path && git checkout -f $1
sleep 10
# need to add in an actual check that the checkout was successful before passing argument
python version_manager_main -su