#!/bin/bash

## series of functions for executing git commands and determining success
# all functions check success of command, and echo True or 0 depending on success of execution. 
# they also return the output from git, which can be saved as an advanced log/feedback for user

## do things need a newline echoed?? 

### SYNTAX GUIDE

## Use variables: platform, easycut, version_manager to specify which repo the function should action in

### REPO PATHS

home_dir="/home/pi/"
easycut_path="${home_dir}easycut-smartbench/"
platform_path="${home_dir}console-raspi3b-plus-platform/"
version_manager_path="${home_dir}smartbench-version-manager/"

go_to_dir(){

	if [[ $1 = "platform" ]]; then
		cd $platform_path
	elif [[ $1 = "easycut" ]]; then
		cd $easycut_path
	# elif [[ $1 = "version_manager" ]]; then
	elif [[ $1 = "version_manager" ]]; then
		cd $version_manager_path
	fi
}

### FETCH

fetch_tags(){

	go_to_dir $1

	# fetch tags from all remotes (including any temporary USB repos)
	if local var=$(git fetch --all -t 2>&1)
	then 
		echo -e $var
		echo -e $\nTrue
	else 
		echo -e $var
		echo -e $\nFalse
	fi
}

### FETCH ALL REPO TAGS (incl. version manager)

fetch_tags_for_all_repos(){

	local platform_success=$(fetch_tags platform)
	local easycut_success=$(fetch_tags easycut)
	local version_manager_success=$(fetch_tags version_manager)

	echo $platform_success
	echo $easycut_success
	echo $version_manager_success

}

get_tag_list(){

	go_to_dir $1
	local var=$(git tag --sort=-refname |head -n 10)
	echo $var
}

### DEBUGGING

fsck_repo(){

	go_to_dir $1

	if local var=$(git fsck --lost-found 2>&1)
	then 
		echo $var
		echo True
	else 
		echo $var
		echo False
	fi
}

### PREPATORY COMMANDS

# set up temporary repository from USB
# arguments: argument 1 is the repo we're setting up for, argument 2 is the usb filepath

set_up_usb_repo(){

	go_to_dir $1

	if local var=$(git remote add temp_repository $2)
	then 
		echo $var
		echo True

	else
		echo $var
		echo False
	fi
}

# set origin URL (just in case)
# argument 1 is the repo, argument 2 is the origin URL
set_origin_URL(){

	go_to_dir $1

	if local var=$(git remote set-url origin $2)
	then 
		echo $var
		echo True

	else
		echo $var
		echo False
	fi
}

# describe current tag & return
current_version(){

	go_to_dir $1

	if local var=$(git describe --tags 2>&1)
	then
		echo $var
		echo True

	else
		echo $var
		echo False

	fi
}


### DO UPDATES

## CHECKOUT NEW VERSIONS

# arg 1 is the repo, arg 2 is the version
checkout_new_version(){

	go_to_dir $1

	if local var=$(git checkout $2 -f 2>&1)
	then
		echo $var
		echo True

	else
		echo $var
		echo False

	fi
}

## PLATFORM ANSIBLE RUN
do_platform_ansible_run(){

	if [ /home/pi/console-raspi3b-plus-platform/ansible/templates/ansible-start.sh ]
	then
		echo 'True'

	else
		echo 'False'

	fi
}


### REPAIR AND BACKUPS

# arguments are 1 = git URL (or bundle to clone), 2 = target directory
clone_backup_repo(){

	if [ -d $2]
	then
		echo "backup directory already exists!"
		echo False
	else
		if local var=$(git clone --bare $1 $2 2>&1)
		then 
			echo $var
			echo True
		else
			echo $var
			echo False

		fi
	fi
}

# set up backups with git clone
clone_backup_repos_from_URL(){

	cd $home_dir

	local platform_success=$(clone_backup_repo "https://github.com/YetiTool/console-raspi3b-plus-platform.git" console-raspi3b-plus-platform-backup)
	local easycut_success=$(clone_backup_repo "https://github.com/YetiTool/easycut-smartbench.git" easycut-smartbench-backup)
	local version_manager_success=$(clone_backup_repo "https://github.com/YetiTool/smartbench-version-manager.git" smartbench-version-manager-backup)

	echo $platform_success
	echo $easycut_success
	echo $version_manager_success

}

# git-repair
repair_repo(){

	go_to_dir $1

	if local var=$(git-repair --force 2>&1)
	then 
		echo $var
		echo True
	else
		echo $var
		
		if local var1=$(sudo aptitude install git-repair)
		then
			if local var2=$(git-repair --force 2>&1)
			then 
				echo $var1
				echo $var2
				echo True
		
			else
				echo $var1
				echo $var2
				echo False
		
			fi
		else
			echo $var1
			echo False

		fi
	fi

}

# git prune
prune_repo(){

	go_to_dir $1

	if local var=$(git prune 2>&1)
	then
		echo $var
		echo True

	else
		echo $var
		echo False

	fi
}

# git gc --aggressive
gc_repo(){

	go_to_dir $1

	if local var=$(git gc --aggressive 2>&1)
	then
		echo $var
		echo True

	else
		echo $var
		echo False

	fi
}
